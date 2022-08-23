import json
from datetime import datetime

import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_socketio import SocketIO, SocketIOTestClient
from mock import patch

from microservice_websocket_docker import app as websocket_app
from microservice_websocket_docker.app import MAX_TRESHOLD, PayloadType, SensorState


class TestFlaskApp:
    @pytest.fixture()
    def app_socketio(self) -> tuple[Flask, SocketIO]:  # type: ignore

        with patch("microservice_websocket_docker.app.DISABLE_MQTT", True):
            app, socketio = websocket_app.create_app()

        app.config.update(
            {
                "TESTING": True,
            }
        )
        app.config.from_file(
            "microservice_websocket_docker/config_testing.json", json.load
        )

        # set up
        yield app, socketio
        # clean up

    @pytest.fixture()
    def app_client(self, app_socketio: tuple[Flask, SocketIO]) -> FlaskClient:
        app, _ = app_socketio
        return app.test_client()

    @pytest.fixture()
    def socketio_client(
        self, app_socketio: tuple[Flask, SocketIO], app_client: FlaskClient
    ) -> SocketIOTestClient:
        app, socketio = app_socketio
        return socketio.test_client(app, flask_test_client=app_client)

    # @patch('microservice_websocket_docker.app.MOBIUS_URL', "")
    # def test_publish_route_post(
    #         self,
    #         app_client,
    #         sensorData_Uplink,
    #         sensorData_noUplink):
    #
    #     response: TestResponse = app_client.post("/publish", json=sensorData_Uplink)
    #     decoded_json: dict = json.loads(response.data)
    #     payload: dict = to_mobius_payload(sensorData_Uplink)
    #
    #     print("[DEBUG] Original data: ")
    #     print(payload)
    #     print("===========================")
    #     print("[DEBUG] Data received back from post request: ")
    #     print(decoded_json)
    #     assert decoded_json == payload, \
    #     "Output mismatch when posting valida data. Check stdout log."
    #
    #     response: TestResponse = app_client.post("/publish", json=sensorData_noUplink)
    #     decoded_json: dict = json.loads(response.data)
    #     assert not decoded_json, \
    #     "Wrong response from post request: should be empty, but it's not"
    #
    # @patch('microservice_websocket_docker.app.MOBIUS_URL', "")
    # def test_main_route_post(self, app_client: FlaskClient, sensorData_Uplink):
    #
    #     body = {
    #         "paths": [sensorData_Uplink["tags"]["sensor_path"]],
    #     }
    #
    #     response: TestResponse = app_client.post("/", json=body)
    #     decoded_json: dict = json.loads(response.data)
    #     assert "data" in decoded_json, "Invalid json from '/' route"
    #     devices: list = decoded_json["data"]
    #     assert len(devices) == len(body["paths"]), \
    #     "Invalid number of devices in json from '/' route"
    #
    # @patch('microservice_websocket_docker.app.MOBIUS_URL', "")
    # def test_socketio_emits_on_change(
    #         self,
    #         app_client: FlaskClient,
    #         socketio_client: SocketIOTestClient,
    #         sensorData_Uplink: dict):
    #     app_client.post("/publish", json=sensorData_Uplink)
    #     received: list = socketio_client.get_received()
    #     assert received[0]['name'] == 'change', \
    #     "Invalid response from socket 'onChange()'"
    #
    # @patch('microservice_websocket_docker.app.MOBIUS_URL', "")
    # def test_get_data(self):
    #     s: dict = websocket_app.get_data("")
    #     print(f"{s=}")
    #     assert all(key in s for key in [
    #             "devEUI",
    #             "applicationID",
    #             "state",
    #             "datiInterni"
    #         ]) and len(s["datiInterni"]) == 3, \
    #     "Invalid structure of returned json: doesn't match `to_irma_ui_data()` \
    #     function, in `data_conversion.py`. Check stdout log."


def _test_update_state_case(
    current: SensorState,
    lastSeenAt: datetime,
    typ: PayloadType,
    dato: int,
    expected: SensorState,
):

    assert (
        got := websocket_app.update_state(current, lastSeenAt, typ, dato)
    ) == expected, f"Error from state '{current}' with timedelta '{datetime.now() - lastSeenAt}',\
    typ '{typ}' and dato '{dato}'. Expected {expected} but got {got}"


def test_get_state():
    # From error
    _test_update_state_case(
        SensorState.ERROR, datetime.now(), PayloadType.READING, 0, SensorState.ERROR
    )
    _test_update_state_case(
        SensorState.ERROR,
        datetime.now(),
        PayloadType.READING,
        MAX_TRESHOLD,
        SensorState.ERROR,
    )
    _test_update_state_case(
        SensorState.ERROR, datetime.now(), PayloadType.START_REC, 0, SensorState.ERROR
    )
    _test_update_state_case(
        SensorState.ERROR, datetime.now(), PayloadType.END_REC, 0, SensorState.ERROR
    )
    _test_update_state_case(
        SensorState.ERROR, datetime.now(), PayloadType.KEEP_ALIVE, 0, SensorState.READY
    )
    _test_update_state_case(
        SensorState.ERROR,
        datetime.now(),
        PayloadType.HANDLE_ALERT,
        0,
        SensorState.ERROR,
    )

    # From ready
    _test_update_state_case(
        SensorState.READY, datetime.now(), PayloadType.READING, 0, SensorState.READY
    )
    _test_update_state_case(
        SensorState.READY,
        datetime.now(),
        PayloadType.READING,
        MAX_TRESHOLD,
        SensorState.ALERT_READY,
    )
    _test_update_state_case(
        SensorState.READY, datetime.now(), PayloadType.START_REC, 0, SensorState.RUNNING
    )
    _test_update_state_case(
        SensorState.READY, datetime.now(), PayloadType.END_REC, 0, SensorState.READY
    )
    _test_update_state_case(
        SensorState.READY, datetime.now(), PayloadType.KEEP_ALIVE, 0, SensorState.READY
    )
    _test_update_state_case(
        SensorState.READY,
        datetime.now(),
        PayloadType.HANDLE_ALERT,
        0,
        SensorState.READY,
    )
    _test_update_state_case(
        SensorState.READY,
        datetime(2020, 6, 1, 3, 2, 1),
        PayloadType.HANDLE_ALERT,
        0,
        SensorState.ERROR,
    )

    # From running
    _test_update_state_case(
        SensorState.RUNNING, datetime.now(), PayloadType.READING, 0, SensorState.RUNNING
    )
    _test_update_state_case(
        SensorState.RUNNING,
        datetime.now(),
        PayloadType.READING,
        MAX_TRESHOLD,
        SensorState.ALERT_RUNNING,
    )
    _test_update_state_case(
        SensorState.RUNNING,
        datetime.now(),
        PayloadType.START_REC,
        0,
        SensorState.RUNNING,
    )
    _test_update_state_case(
        SensorState.RUNNING, datetime.now(), PayloadType.END_REC, 0, SensorState.READY
    )
    _test_update_state_case(
        SensorState.RUNNING,
        datetime.now(),
        PayloadType.KEEP_ALIVE,
        0,
        SensorState.RUNNING,
    )
    _test_update_state_case(
        SensorState.RUNNING,
        datetime.now(),
        PayloadType.HANDLE_ALERT,
        0,
        SensorState.RUNNING,
    )

    # From alert_ready
    _test_update_state_case(
        SensorState.ALERT_READY,
        datetime.now(),
        PayloadType.READING,
        0,
        SensorState.ALERT_READY,
    )
    _test_update_state_case(
        SensorState.ALERT_READY,
        datetime.now(),
        PayloadType.START_REC,
        0,
        SensorState.ALERT_READY,
    )
    _test_update_state_case(
        SensorState.ALERT_READY,
        datetime.now(),
        PayloadType.END_REC,
        0,
        SensorState.ALERT_READY,
    )
    _test_update_state_case(
        SensorState.ALERT_READY,
        datetime.now(),
        PayloadType.KEEP_ALIVE,
        0,
        SensorState.ALERT_READY,
    )
    _test_update_state_case(
        SensorState.ALERT_READY,
        datetime.now(),
        PayloadType.HANDLE_ALERT,
        0,
        SensorState.READY,
    )
    _test_update_state_case(
        SensorState.ALERT_READY,
        datetime(2020, 6, 1, 3, 2, 1),
        PayloadType.HANDLE_ALERT,
        0,
        SensorState.ERROR,
    )

    # From alert_running
    _test_update_state_case(
        SensorState.ALERT_RUNNING,
        datetime.now(),
        PayloadType.READING,
        0,
        SensorState.ALERT_RUNNING,
    )
    _test_update_state_case(
        SensorState.ALERT_RUNNING,
        datetime.now(),
        PayloadType.START_REC,
        0,
        SensorState.ALERT_RUNNING,
    )
    _test_update_state_case(
        SensorState.ALERT_RUNNING,
        datetime.now(),
        PayloadType.END_REC,
        0,
        SensorState.ALERT_READY,
    )
    _test_update_state_case(
        SensorState.ALERT_RUNNING,
        datetime.now(),
        PayloadType.KEEP_ALIVE,
        0,
        SensorState.ALERT_RUNNING,
    )
    _test_update_state_case(
        SensorState.ALERT_RUNNING,
        datetime.now(),
        PayloadType.HANDLE_ALERT,
        0,
        SensorState.RUNNING,
    )


def test_decode_data():
    encoded_data: str = "AQAAAAdtb2JpdXNJZCAgbW9iaXVzUGF0aA=="

    expected_output = {
        "payloadType": 1,
        "sensorData": 7,
        "mobius_sensorId": "mobiusId",
        "mobius_sensorPath": "mobiusPath"
    }

    assert websocket_app.decode_data(encoded_data) == expected_output, \
    "Error in `decode_data`: output mismatch"


def test_encode_mqtt_data():
    command: int = 1
    iso_timestamp: str = "2022-08-23T11:06:00.676497"

    expected_output: bytes = b'ATIwMjItMDgtMjNUMTE6MDY6MDAuNjc2NDk3'

    assert websocket_app.encode_mqtt_data(command, iso_timestamp) == expected_output, \
    "Error in `encode_mqtt_data`: output mismatch"


def test_to_irma_ui():
    sensorID = "2288300834"
    sensorName = "123"
    applicationID = "123234"
    state = "ok"
    titolo1 = "Foo"
    titolo2 = "Bar"
    titolo3 = "Baz"
    dato1 = 0.0
    dato2 = 0.0
    dato3 = 0
    unhandledAlertIDs = [1, 2, 3, 4]

    expected_value = {
        "sensorID": sensorID,
        "sensorName": sensorName,
        "applicationID": applicationID,
        "state": state,
        "datiInterni": [
            {"titolo": titolo1, "dato": dato1},
            {"titolo": titolo2, "dato": dato2},
            {"titolo": titolo3, "dato": dato3},
        ],
        "unhandledAlertIDs": unhandledAlertIDs,
    }

    assert (
        websocket_app.to_irma_ui_data(
            sensorID,
            sensorName,
            applicationID,
            state,
            titolo1,
            titolo2,
            titolo3,
            dato1,
            dato2,
            dato3,
            unhandledAlertIDs,
        )
        == expected_value
    ), "Error in `to_irma_ui_data`: output mismatch"
