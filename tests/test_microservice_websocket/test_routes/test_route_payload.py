import pytest
from flask.testing import FlaskClient
from mock import mock_open, patch

from microservice_websocket.app.services import database as db
from microservice_websocket.app.utils.enums import NodeState, PayloadType

# TODO: ALERT_TRESHOLD from configs


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
        db.Alert.drop_collection()
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

    # Post all window readings
    def test_publish_window_readings(self, app_client: FlaskClient):
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

    # Create reading by sending windows first
    def test_publish_windows_first(self, app_client: FlaskClient):
        data_w1 = {
            "canID": 1,
            "sensorNumber": 2,
            "value": 1,
            "count": 111,
            "sessionID": 5,
            "readingID": 7,
        }

        data_w2 = {
            "canID": 1,
            "sensorNumber": 2,
            "value": 2,
            "count": 222,
            "sessionID": 5,
            "readingID": 7,
        }

        data_w3 = {
            "canID": 1,
            "sensorNumber": 2,
            "value": 3,
            "count": 333,
            "sessionID": 5,
            "readingID": 7,
        }

        data_total = {
            "canID": 1,
            "sensorNumber": 2,
            "value": 4,
            "count": 777,
            "sessionID": 5,
            "readingID": 7,
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

            response = app_client.post(
                self.endpoint,
                json={
                    "nodeID": 123,
                    "nodeName": "nodeName",
                    "applicationID": str(db.Application.objects().first()["id"]),
                    "organizationID": str(db.Organization.objects().first()["id"]),
                    "payloadType": PayloadType.TOTAL_READING,
                    "data": data_total,
                },
                headers={"Authorization": "Bearer 1234"},
            )

            assert (
                response.status_code == 200
            ), "Invalid response code when publishing valid payload"

            assert len(db.Node.objects()) == 1, "Invalid number of Node"
            assert len(db.Reading.objects()) == 2, "Invalid number of Reading"

            reading = db.Reading.objects(sessionID=5).first()
            assert (
                reading["dangerLevel"] == 4
                and reading["window1_count"] == 111
                and reading["window2_count"] == 222
                and reading["window3_count"] == 333
            ), "Invalid Reading structure"

    # Publish reading with dangerLevel > ALERT_TRESHOLD
    def test_publish_alert_from_state_ok(self, app_client: FlaskClient):
        with patch("builtins.open", mock_open(read_data="1234")):
            response = app_client.post(
                self.endpoint,
                json={
                    "nodeID": 123,
                    "nodeName": "nodeName",
                    "applicationID": str(db.Application.objects().first()["id"]),
                    "organizationID": str(db.Organization.objects().first()["id"]),
                    "payloadType": PayloadType.TOTAL_READING,
                    "data": {
                        "canID": 1,
                        "sensorNumber": 2,
                        "value": 9,
                        "count": 777,
                        "sessionID": 6,
                        "readingID": 9,
                    },
                },
                headers={"Authorization": "Bearer 1234"},
            )

        assert (
            response.status_code == 200
        ), "Invalid response code when publishing valid payload"

        assert len(db.Reading.objects()) == 3, "Invalid number of Reading"
        assert len(db.Alert.objects()) == 1, "Invalid number of Alert"
        assert (
            db.Node.objects().first()["state"] == NodeState.ALERT_RUNNING
        ), "Invalid Node state"

    # Publish reading with dangerLevel > ALERT_TRESHOLD while already in alert
    def test_publish_alert_from_state_alert_running(self, app_client: FlaskClient):
        with patch("builtins.open", mock_open(read_data="1234")):
            response = app_client.post(
                self.endpoint,
                json={
                    "nodeID": 123,
                    "nodeName": "nodeName",
                    "applicationID": str(db.Application.objects().first()["id"]),
                    "organizationID": str(db.Organization.objects().first()["id"]),
                    "payloadType": PayloadType.TOTAL_READING,
                    "data": {
                        "canID": 1,
                        "sensorNumber": 2,
                        "value": 9,
                        "count": 777,
                        "sessionID": 6,
                        "readingID": 11,
                    },
                },
                headers={"Authorization": "Bearer 1234"},
            )

        assert (
            response.status_code == 200
        ), "Invalid response code when publishing valid payload"

        assert len(db.Reading.objects()) == 4, "Invalid number of Reading"
        assert len(db.Alert.objects()) == 1, "Invalid number of Alert"
        assert (
            db.Node.objects().first()["state"] == NodeState.ALERT_RUNNING
        ), "Invalid Node state"

    # Publish reading with dangerLevel > ALERT_TRESHOLD with an already handled alert
    def test_publish_alert_with_already_handled_alert(self, app_client: FlaskClient):
        alert = db.Alert.objects().first()
        alert["isHandled"] = True
        alert.save()

        node = db.Node.objects().first()
        node["state"] = NodeState.READY
        node.save()

        with patch("builtins.open", mock_open(read_data="1234")):
            response = app_client.post(
                self.endpoint,
                json={
                    "nodeID": 123,
                    "nodeName": "nodeName",
                    "applicationID": str(db.Application.objects().first()["id"]),
                    "organizationID": str(db.Organization.objects().first()["id"]),
                    "payloadType": PayloadType.TOTAL_READING,
                    "data": {
                        "canID": 1,
                        "sensorNumber": 2,
                        "value": 9,
                        "count": 777,
                        "sessionID": 6,
                        "readingID": 12,
                    },
                },
                headers={"Authorization": "Bearer 1234"},
            )

        assert (
            response.status_code == 200
        ), "Invalid response code when publishing valid payload"

        assert len(db.Reading.objects()) == 5, "Invalid number of Reading"
        assert len(db.Alert.objects()) == 2, "Invalid number of Alert"
        assert (
            db.Node.objects().first()["state"] == NodeState.ALERT_RUNNING
        ), "Invalid Node state"

    def test_publish_window_reading_wrong_value(self, app_client: FlaskClient):
        with patch("builtins.open", mock_open(read_data="1234")):
            with pytest.raises(ValueError):
                response = app_client.post(
                    self.endpoint,
                    json={
                        "nodeID": 123,
                        "nodeName": "nodeName",
                        "applicationID": str(db.Application.objects().first()["id"]),
                        "organizationID": str(db.Organization.objects().first()["id"]),
                        "payloadType": PayloadType.WINDOW_READING,
                        "data": {
                            "canID": 1,
                            "sensorNumber": 2,
                            "value": 5,
                            "count": 333,
                            "sessionID": 5,
                            "readingID": 1,
                        },
                    },
                    headers={"Authorization": "Bearer 1234"},
                )
                assert (
                    response.status_code == 500
                ), "Invalid response code when publishing window with wrong value"

    # Publish leftover payload types
    def test_publish_remaining_payloads(self, app_client: FlaskClient):
        with patch("builtins.open", mock_open(read_data="1234")):
            for type in [
                PayloadType.KEEP_ALIVE,
                PayloadType.START_REC,
                PayloadType.END_REC,
            ]:
                response = app_client.post(
                    self.endpoint,
                    json={
                        "nodeID": 123,
                        "nodeName": "nodeName",
                        "applicationID": str(db.Application.objects().first()["id"]),
                        "organizationID": str(db.Organization.objects().first()["id"]),
                        "payloadType": type,
                        "data": {},
                    },
                    headers={"Authorization": "Bearer 1234"},
                )

            assert (
                response.status_code == 200
            ), "Invalid response code when publishing valid payload"
