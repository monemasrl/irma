import pytest
from fastapi.testclient import TestClient
from mock import mock_open, patch

from microservice_websocket.app.services import database as db
from microservice_websocket.app.utils.enums import NodeState, PayloadType


class TestPublishPayload:
    endpoint = "/api/payload/publish"

    # Trying to post data to non-existing application
    @pytest.mark.asyncio
    async def test_publish_not_existing_app(self, app_client: TestClient):
        org = db.Organization(organizationName="foo")
        await org.save()
        # Done setup

        with patch("builtins.open", mock_open(read_data="1234")):
            response = app_client.post(
                self.endpoint,
                json={
                    "nodeID": 123,
                    "nodeName": "nodeName",
                    "applicationID": "63186eab0ca2d54a5c258384",
                    "organizationID": str(org.id),
                    "payloadType": PayloadType.KEEP_ALIVE,
                    "data": None,
                },
                headers={"Authorization": "Bearer 1234"},
            )

        assert (
            response.status_code == 404
        ), "Invalid response code when posting data to non-existing application"

    # Post data to non-existing node
    @pytest.mark.asyncio
    async def test_publish_not_existing_node(self, app_client: TestClient):
        org = db.Organization(organizationName="foo")
        await org.save()
        app = db.Application(applicationName="bar", organization=org.id)
        await app.save()
        # Done setup

        total_reading_data = {
            "canID": 1,
            "sensorNumber": 2,
            "value": 3,
            "count": 111,
            "sessionID": 3,
            "readingID": 1,
        }

        with (
            patch("builtins.open", mock_open(read_data="1234")),
            patch("socketio.Client.emit", return_value=None),
        ):
            response = app_client.post(
                self.endpoint,
                json={
                    "nodeID": 123,
                    "nodeName": "nodeName",
                    "applicationID": str(app.id),
                    "organizationID": str(org.id),
                    "payloadType": PayloadType.TOTAL_READING,
                    "data": total_reading_data,
                },
                headers={"Authorization": "Bearer 1234"},
            )

        assert (
            response.status_code == 200
        ), "Invalid response code when publishing valid payload"
        assert (
            len(await db.Node.find_all().to_list()) == 1
        ), "Couldn't create node upon posting data"
        assert (
            len(await db.Reading.find_all().to_list()) == 1
        ), "Couldn't create reading upon posting data"

    # Post all window readings
    @pytest.mark.asyncio
    async def test_publish_window_readings(self, app_client: TestClient):
        org = db.Organization(organizationName="foo")
        await org.save()
        app = db.Application(applicationName="bar", organization=org.id)
        await app.save()
        total_reading_data = {
            "canID": 1,
            "sensorNumber": 2,
            "value": 3,
            "count": 111,
            "sessionID": 3,
            "readingID": 1,
        }

        with (
            patch("builtins.open", mock_open(read_data="1234")),
            patch("socketio.Client.emit", return_value=None),
        ):
            response = app_client.post(
                self.endpoint,
                json={
                    "nodeID": 123,
                    "nodeName": "nodeName",
                    "applicationID": str(app.id),
                    "organizationID": str(org.id),
                    "payloadType": PayloadType.TOTAL_READING,
                    "data": total_reading_data,
                },
                headers={"Authorization": "Bearer 1234"},
            )
        # Done setup

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

        with (
            patch("builtins.open", mock_open(read_data="1234")),
            patch("socketio.Client.emit", return_value=None),
        ):
            for data in [data_w1, data_w2, data_w3]:
                response = app_client.post(
                    self.endpoint,
                    json={
                        "nodeID": 123,
                        "nodeName": "nodeName",
                        "applicationID": str(app.id),
                        "organizationID": str(org.id),
                        "payloadType": PayloadType.WINDOW_READING,
                        "data": data,
                    },
                    headers={"Authorization": "Bearer 1234"},
                )

                assert (
                    response.status_code == 200
                ), "Invalid response code when publishing valid payload"

        assert len(await db.Node.find_all().to_list()) == 1, "Invalid node count"
        assert (
            len(await db.Reading.find_all().to_list()) == 1
        ), "Couldn't merge readings with same readingID, canID and sensorNumber"

        reading = await db.Reading.find_one()
        assert reading

        assert (
            reading.dangerLevel == 3
            and reading.window1 == 111
            and reading.window2 == 222
            and reading.window3 == 333
        ), "Invalid reading merge"

    # Create reading by sending windows first
    @pytest.mark.asyncio
    async def test_publish_windows_first(self, app_client: TestClient):
        org = db.Organization(organizationName="foo")
        await org.save()
        app = db.Application(applicationName="bar", organization=org.id)
        await app.save()
        # Done setup

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

        with (
            patch("builtins.open", mock_open(read_data="1234")),
            patch("socketio.Client.emit", return_value=None),
        ):
            for data in [data_w1, data_w2, data_w3]:
                response = app_client.post(
                    self.endpoint,
                    json={
                        "nodeID": 123,
                        "nodeName": "nodeName",
                        "applicationID": str(app.id),
                        "organizationID": str(org.id),
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
                    "applicationID": str(app.id),
                    "organizationID": str(org.id),
                    "payloadType": PayloadType.TOTAL_READING,
                    "data": data_total,
                },
                headers={"Authorization": "Bearer 1234"},
            )

            assert (
                response.status_code == 200
            ), "Invalid response code when publishing valid payload"

            assert (
                len(await db.Node.find_all().to_list()) == 1
            ), "Invalid number of Node"
            assert (
                len(await db.Reading.find_all().to_list()) == 1
            ), "Invalid number of Reading"

            reading = await db.Reading.find_one(db.Reading.sessionID == 5)
            assert reading

            assert (
                reading.dangerLevel == 4
                and reading.window1 == 111
                and reading.window2 == 222
                and reading.window3 == 333
            ), "Invalid Reading structure"

    # Publish reading with dangerLevel > ALERT_TRESHOLD
    @pytest.mark.asyncio
    async def test_publish_alert_from_state_ok(self, app_client: TestClient):
        org = db.Organization(organizationName="foo")
        await org.save()
        app = db.Application(applicationName="bar", organization=org.id)
        await app.save()
        # Done setup

        with (
            patch("builtins.open", mock_open(read_data="1234")),
            patch("socketio.Client.emit", return_value=None),
        ):
            response = app_client.post(
                self.endpoint,
                json={
                    "nodeID": 123,
                    "nodeName": "nodeName",
                    "applicationID": str(app.id),
                    "organizationID": str(org.id),
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

        assert (
            len(await db.Reading.find_all().to_list()) == 1
        ), "Invalid number of Reading"
        assert len(await db.Alert.find_all().to_list()) == 1, "Invalid number of Alert"
        assert (
            node := await db.Node.find_one()
        ) and node.state == NodeState.ALERT_RUNNING, "Invalid Node state"

    # Publish reading with dangerLevel > ALERT_TRESHOLD while already in alert
    @pytest.mark.asyncio
    async def test_publish_alert_from_state_alert_running(self, app_client: TestClient):
        org = db.Organization(organizationName="foo")
        await org.save()
        app = db.Application(applicationName="bar", organization=org.id)
        await app.save()
        # Done setup

        with (
            patch("builtins.open", mock_open(read_data="1234")),
            patch("socketio.Client.emit", return_value=None),
        ):
            response = app_client.post(
                self.endpoint,
                json={
                    "nodeID": 123,
                    "nodeName": "nodeName",
                    "applicationID": str(app.id),
                    "organizationID": str(org.id),
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

        assert (
            len(await db.Reading.find_all().to_list()) == 1
        ), "Invalid number of Reading"
        assert len(await db.Alert.find_all().to_list()) == 1, "Invalid number of Alert"
        assert (
            node := await db.Node.find_one()
        ) and node.state == NodeState.ALERT_RUNNING, "Invalid Node state"

    # Publish reading with dangerLevel > ALERT_TRESHOLD with an already handled alert
    @pytest.mark.asyncio
    async def test_publish_alert_with_already_handled_alert(
        self, app_client: TestClient
    ):
        org = db.Organization(organizationName="foo")
        await org.save()
        app = db.Application(applicationName="bar", organization=org.id)
        await app.save()

        with (
            patch("builtins.open", mock_open(read_data="1234")),
            patch("socketio.Client.emit", return_value=None),
        ):
            response = app_client.post(
                self.endpoint,
                json={
                    "nodeID": 123,
                    "nodeName": "nodeName",
                    "applicationID": str(app.id),
                    "organizationID": str(org.id),
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
        # Done setup

        alert = await db.Alert.find_one()
        assert alert
        alert.isHandled = True
        await alert.save()

        node = await db.Node.find_one()
        assert node
        node.state = NodeState.READY
        await node.save()

        with (
            patch("builtins.open", mock_open(read_data="1234")),
            patch("socketio.Client.emit", return_value=None),
        ):
            response = app_client.post(
                self.endpoint,
                json={
                    "nodeID": 123,
                    "nodeName": "nodeName",
                    "applicationID": str(app.id),
                    "organizationID": str(org.id),
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

        assert (
            len(await db.Reading.find_all().to_list()) == 2
        ), "Invalid number of Reading"
        assert len(await db.Alert.find_all().to_list()) == 2, "Invalid number of Alert"
        assert (
            node := await db.Node.find_one()
        ) and node.state == NodeState.ALERT_RUNNING, "Invalid Node state"

    @pytest.mark.asyncio
    async def test_publish_window_reading_wrong_value(self, app_client: TestClient):
        org = db.Organization(organizationName="foo")
        await org.save()
        app = db.Application(applicationName="bar", organization=org.id)
        await app.save()
        # Done setup

        with patch("builtins.open", mock_open(read_data="1234")):
            with pytest.raises(ValueError):
                response = app_client.post(
                    self.endpoint,
                    json={
                        "nodeID": 123,
                        "nodeName": "nodeName",
                        "applicationID": str(app.id),
                        "organizationID": str(org.id),
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
    @pytest.mark.asyncio
    async def test_publish_remaining_payloads(self, app_client: TestClient):
        org = db.Organization(organizationName="foo")
        await org.save()
        app = db.Application(applicationName="bar", organization=org.id)
        await app.save()
        # Done setup

        with (
            patch("builtins.open", mock_open(read_data="1234")),
            patch("socketio.Client.emit", return_value=None),
        ):

            for typ in [
                PayloadType.KEEP_ALIVE,
                PayloadType.START_REC,
                PayloadType.END_REC,
            ]:
                response = app_client.post(
                    self.endpoint,
                    json={
                        "nodeID": 123,
                        "nodeName": "nodeName",
                        "applicationID": str(app.id),
                        "organizationID": str(org.id),
                        "payloadType": typ,
                        "data": None,
                    },
                    headers={"Authorization": "Bearer 1234"},
                )

                assert (
                    response.status_code == 200
                ), "Invalid response code when publishing valid payload"
