from datetime import datetime

from flask.testing import FlaskClient

from microservice_websocket.app.services import database as db


class TestGetSessions:
    endpoint = "/api/session/"

    @classmethod
    def setup_class(cls):
        o = db.Organization(organizationName="orgName")
        o.save()
        a = db.Application(applicationName="appName", organization=o)
        a.save()

    @classmethod
    def teardown_class(cls):
        db.Reading.drop_collection()
        db.Node.drop_collection()
        db.Application.drop_collection()
        db.Organization.drop_collection()

    # Get without args
    def test_get_no_args(self, app_client: FlaskClient, auth_header):
        response = app_client.get(self.endpoint, headers=auth_header)

        assert (
            response.status_code == 400
        ), "Invalid response code when getting sessions with no nodeID"

    # Get session of non existing node
    def test_get_non_existing_node(self, app_client: FlaskClient, auth_header):
        response = app_client.get(
            self.endpoint, headers=auth_header, query_string={"nodeID": 100}
        )

        assert (
            response.status_code == 404
        ), "Invalid response code when trying to get session of non existing node"

    # Get whene there's no session
    def test_get_no_session(self, app_client: FlaskClient, auth_header):
        node = db.Node(
            nodeID=123,
            nodeName="nodeName",
            application=db.Application.objects().first(),
            organization=db.Organization.objects().first(),
            state=1,
            lastSeenAt=datetime.now(),
        )
        node.save()

        response = app_client.get(
            self.endpoint, headers=auth_header, query_string={"nodeID": 123}
        )

        assert (
            response.status_code == 200
        ), "Invalid response code when getting session from valid node"

        assert len(response.json["readings"]) == 0, "Invalid readings length"

    # Get the latest session
    def test_get_latest_session(self, app_client: FlaskClient, auth_header):
        r1 = db.Reading(
            nodeID=db.Node.objects().first()["nodeID"],
            canID=1,
            sensorNumber=1,
            readingID=1,
            sessionID=1,
            publishedAt=datetime.now(),
        )
        r1.save()
        r2 = db.Reading(
            nodeID=db.Node.objects().first()["nodeID"],
            canID=2,
            sensorNumber=1,
            readingID=1,
            sessionID=2,
            publishedAt=datetime.now(),
        )
        r2.save()
        r3 = db.Reading(
            nodeID=db.Node.objects().first()["nodeID"],
            canID=3,
            sensorNumber=1,
            readingID=1,
            sessionID=3,
            publishedAt=datetime.now(),
        )
        r3.save()

        response = app_client.get(
            self.endpoint,
            headers=auth_header,
            query_string={"nodeID": db.Node.objects().first()["nodeID"]},
        )

        assert (
            response.status_code == 200
        ), "Invalid response code when querying latest session"

        assert (
            response.json["readings"][0]["canID"] == 3
        ), "Invalid response when querying latest session"

    def test_get_specific_session(self, app_client: FlaskClient, auth_header):
        response = app_client.get(
            self.endpoint,
            headers=auth_header,
            query_string={
                "nodeID": db.Node.objects().first()["nodeID"],
                "sessionID": 2,
            },
        )

        assert (
            response.status_code == 200
        ), "Invalid response code when querying specific session"

        assert (
            response.json["readings"][0]["canID"] == 2
        ), "Invalid response when querying specific session"


class TestGetSessionID:
    endpoint = "/api/session/ids"

    @classmethod
    def setup_class(cls):
        o = db.Organization(organizationName="orgName")
        o.save()
        a = db.Application(applicationName="appName", organization=o)
        a.save()

    @classmethod
    def teardown_class(cls):
        db.Reading.drop_collection()
        db.Node.drop_collection()
        db.Application.drop_collection()
        db.Organization.drop_collection()

    # Get sessionIDs without args
    def test_get_no_args(self, app_client: FlaskClient, auth_header):
        response = app_client.get(self.endpoint, headers=auth_header)

        assert (
            response.status_code == 400
        ), "Invalid response code when submitting no args"

    # Get sessionIDs of non existings node
    def test_get_non_existing_node(self, app_client: FlaskClient, auth_header):
        response = app_client.get(
            self.endpoint, headers=auth_header, query_string={"nodeID": 100}
        )

        assert (
            response.status_code == 404
        ), "Invalid response code when getting sessionIDs of non existring Node"

    # Get sessionIDs with no readings
    def test_get_no_ids(self, app_client: FlaskClient, auth_header):
        node = db.Node(
            nodeID=123,
            nodeName="nodeName",
            application=db.Application.objects().first(),
            organization=db.Organization.objects().first(),
            state=1,
            lastSeenAt=datetime.now(),
        )
        node.save()

        response = app_client.get(
            self.endpoint,
            headers=auth_header,
            query_string={"nodeID": db.Node.objects().first()["nodeID"]},
        )

        assert (
            response.status_code == 200
        ), "Invalid response code when getting sessionIDs from valid Node"

        assert (
            len(response.json["IDs"]) == 0
        ), "Invalid response when getting sessionIDs from valid Node"

    # Get sessionIDs
    def test_get(self, app_client: FlaskClient, auth_header):
        r1 = db.Reading(
            nodeID=db.Node.objects().first()["nodeID"],
            canID=1,
            sensorNumber=1,
            readingID=1,
            sessionID=1,
            publishedAt=datetime.now(),
        )
        r1.save()
        r2 = db.Reading(
            nodeID=db.Node.objects().first()["nodeID"],
            canID=2,
            sensorNumber=1,
            readingID=1,
            sessionID=2,
            publishedAt=datetime.now(),
        )
        r2.save()

        response = app_client.get(
            self.endpoint,
            headers=auth_header,
            query_string={"nodeID": db.Node.objects().first()["nodeID"]},
        )

        assert (
            response.status_code == 200
        ), "Invalid response code when getting sessionIDs from valid Node"

        assert (
            len(response.json["IDs"]) == 2
        ), "Invalid response when getting sessionIDs from valid Node"
