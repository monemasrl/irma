from flask.testing import FlaskClient
from mock import mock_open, patch

from microservice_websocket.app.services import database as db
from microservice_websocket.app.utils.enums import PayloadType


class TestPublishPayload:
    endpoint = "/api/payload/publish"

    @classmethod
    def setup_class(cls):
        # Leftover reading ???
        db.Reading.drop_collection()

        org = db.Organization(organizationName="foo")
        org.save()
        app = db.Application(applicationName="bar", organization=org)
        app.save()

    @classmethod
    def teardown_class(cls):
        db.Reading.drop_collection()
        db.Node.drop_collection()
        db.Application.drop_collection()
        db.Organization.drop_collection()

    # Trying to post data to non-existing application
    def test_publish_not_existing_app(self, app_client: FlaskClient):
        with patch("builtins.open", mock_open(read_data="1234")):
            response = app_client.post(
                self.endpoint,
                json={
                    "nodeID": 123,
                    "nodeName": "nodeName",
                    "applicationID": "63186eab0ca2d54a5c258384",
                    "organizationID": str(db.Organization.objects().first()["id"]),
                    "payloadType": PayloadType.KEEP_ALIVE,
                    "data": {},
                },
                headers={"Authorization": "Bearer 1234"},
            )

        assert (
            response.status_code == 404
        ), "Invalid response code when posting data to non-existing application"

    # Post data to non-existing node
    def test_publish_not_existing_node(self, app_client: FlaskClient):
        total_reading_data = {
            "canID": 1,
            "sensorNumber": 2,
            "value": 3,
            "count": 111,
            "sessionID": 3,
            "readingID": 1,
        }

        with patch("builtins.open", mock_open(read_data="1234")):
            response = app_client.post(
                self.endpoint,
                json={
                    "nodeID": 123,
                    "nodeName": "nodeName",
                    "applicationID": str(db.Application.objects().first()["id"]),
                    "organizationID": str(db.Organization.objects().first()["id"]),
                    "payloadType": PayloadType.TOTAL_READING,
                    "data": total_reading_data,
                },
                headers={"Authorization": "Bearer 1234"},
            )

        assert (
            response.status_code == 200
        ), "Invalid response code when publishing valid payload"
        assert len(db.Node.objects()) == 1, "Couldn't create node upon posting data"
        assert (
            len(db.Reading.objects()) == 1
        ), "Couldn't create reading upon posting data"

    # Post all type of reading
    def test_publish_all_readings(self, app_client: FlaskClient):
        data_w1 = {
            "canID": 1,
            "sensorNumber": 2,
            "value": 1,
            "count": 111,
            "sessionID": 3,
            "readingID": 1,
        }

        data_w2 = {
            "canID": 1,
            "sensorNumber": 2,
            "value": 2,
            "count": 222,
            "sessionID": 3,
            "readingID": 1,
        }

        data_w3 = {
            "canID": 1,
            "sensorNumber": 2,
            "value": 3,
            "count": 333,
            "sessionID": 3,
            "readingID": 1,
        }

        with patch("builtins.open", mock_open(read_data="1234")):
            for data in [data_w1, data_w2, data_w3]:
                response = app_client.post(
                    self.endpoint,
                    json={
                        "nodeID": 123,
                        "nodeName": "nodeName",
                        "applicationID": str(db.Application.objects().first()["id"]),
                        "organizationID": str(db.Organization.objects().first()["id"]),
                        "payloadType": PayloadType.WINDOW_READING,
                        "data": data,
                    },
                    headers={"Authorization": "Bearer 1234"},
                )

            assert (
                response.status_code == 200
            ), "Invalid response code when publishing valid payload"

        assert len(db.Node.objects()) == 1, "Invalid node count"
        assert (
            len(db.Reading.objects()) == 1
        ), "Couldn't merge readings with same readingID, canID and sensorNumber"

        reading = db.Reading.objects().first()

        assert (
            reading["dangerLevel"] == 3
            and reading["window1_count"] == 111
            and reading["window2_count"] == 222
            and reading["window3_count"] == 333
        ), "Invalid reading merge"
