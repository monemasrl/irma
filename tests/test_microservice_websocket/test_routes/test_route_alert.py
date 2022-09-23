from datetime import datetime

from flask.testing import FlaskClient

from microservice_websocket.app.services import database as db
from microservice_websocket.app.utils.enums import NodeState


class TestAlertHandle:
    endpoint = "/api/alert/handle"

    @classmethod
    def setup_class(cls):
        # Leftover readings ???
        db.Reading.drop_collection()

        org = db.Organization(organizationName="foo")
        org.save()
        app = db.Application(applicationName="bar", organization=org)
        app.save()
        node = db.Node(
            nodeID=123,
            nodeName="nodeName",
            application=app,
            organization=org,
            state=NodeState.ALERT_READY,
            lastSeenAt=datetime.now(),
        )
        node.save()
        reading = db.Reading(
            nodeID=node["nodeID"],
            canID=1,
            sensorNumber=2,
            readingID=32704,
            sessionID=12892,
            publishedAt=datetime.now(),
        )
        reading.save()

    @classmethod
    def teardown_class(cls):
        db.Alert.drop_collection()
        db.Reading.drop_collection()
        db.Node.drop_collection()
        db.Application.drop_collection()
        db.Organization.drop_collection()

    # Handle not existing alert
    def test_handle_not_existing(self, app_client: FlaskClient, auth_header):

        response = app_client.post(
            self.endpoint,
            json={
                "alertID": "63186eab0ca2d54a5c258384",
                "isConfirmed": True,
                "handleNote": "foo",
            },
            headers=auth_header,
        )

        assert (
            response.status_code == 404
        ), "Invalid response code when trying to handle non-existing alert"

    def test_handle(self, app_client: FlaskClient, auth_header):
        reading = db.Reading.objects().first()

        # Manually create Alerts
        alert = db.Alert(
            reading=reading,
            node=db.Node.objects().first(),
            sessionID=reading["sessionID"],
            isHandled=False,
        )
        alert.save()
        alert2 = db.Alert(
            reading=reading,
            node=db.Node.objects().first(),
            sessionID=reading["sessionID"],
            isHandled=False,
        )
        alert2.save()

        # Try to handle newly created alert
        response = app_client.post(
            self.endpoint,
            json={
                "alertID": str(alert["id"]),
                "isConfirmed": True,
                "handleNote": "foo",
            },
            headers=auth_header,
        )

        alert = db.Alert.objects(id=alert["id"]).first()

        assert (
            response.status_code == 200
            and alert["isConfirmed"]
            and alert["handleNote"] == "foo"
            and alert["handledBy"]["email"] == "bettarini@monema.it"
        ), "Invalid response code when trying to handle existing alert"

        assert (
            db.Node.objects().first()["state"] == NodeState.ALERT_READY
        ), "Invalid state when handling 1/2 alert"

        # Handle leftover alert
        response = app_client.post(
            self.endpoint,
            json={
                "alertID": str(alert2["id"]),
                "isConfirmed": True,
                "handleNote": "foo",
            },
            headers=auth_header,
        )

        assert (
            db.Node.objects().first()["state"] == NodeState.READY
        ), "Invalid state when handling all alert"
