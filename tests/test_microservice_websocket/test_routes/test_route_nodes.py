from datetime import datetime

from flask.testing import FlaskClient

from microservice_websocket.app.services import database as db


class TestGetNodes:
    endpoint = "/api/nodes/"
    name = "nodeName"

    @classmethod
    def setup_class(cls):
        o = db.Organization(organizationName="foo")
        o.save()
        a = db.Application(applicationName="bar", organization=o)
        a.save()

    @classmethod
    def teardown_class(cls):
        db.Node.drop_collection()
        db.Application.drop_collection()
        db.Organization.drop_collection()

    # Getting nodes with no args
    def test_get_no_args(self, app_client: FlaskClient, auth_header):
        response = app_client.get(self.endpoint, headers=auth_header)

        assert (
            response.status_code == 400
        ), "Invalid response code when getting node with no args"

    # Getting nodes with no node present
    def test_get_no_nodes(self, app_client: FlaskClient, auth_header):
        applicationID = str(db.Application.objects().first()["id"])

        response = app_client.get(
            self.endpoint,
            headers=auth_header,
            query_string={"applicationID": applicationID},
        )

        assert (
            response.status_code == 404
        ), "Invalid response code when getting empty nodes"

    def test_get(self, app_client: FlaskClient, auth_header):
        applicationID = str(db.Application.objects().first()["id"])

        # Manually create node
        n = db.Node(
            nodeID=123,
            nodeName=self.name,
            application=db.Application.objects().first(),
            organization=db.Organization.objects().first(),
            state=1,
            lastSeenAt=datetime.now(),
        )
        n.save()

        # Getting newly created node
        response = app_client.get(
            self.endpoint,
            headers=auth_header,
            query_string={"applicationID": applicationID},
        )

        assert response.status_code == 200, "Invalid response code when getting nodes"

        assert response.json["nodes"][0]["nodeName"] == self.name
