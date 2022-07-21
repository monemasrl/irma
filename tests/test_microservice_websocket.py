from flask_socketio import SocketIO, SocketIOTestClient
from flask import Flask
from flask.testing import FlaskClient
from werkzeug.test import TestResponse
from mock import patch
from microservice_websocket_docker import app as websocket_app
from microservice_websocket_docker.app import SensorState, PayloadType, MAX_TRESHOLD
import pytest
import json
from fixtures.data_fixtures import *


class TestFlaskApp:

    @pytest.fixture()
    def app_socketio(self) -> tuple[Flask, SocketIO]: # type: ignore

        with patch('microservice_websocket_docker.app.DISABLE_MQTT', True):
            app, socketio = websocket_app.create_app()

        app.config.update({
            "TESTING": True,
        })
        app.config.from_file("microservice_websocket_docker/config_testing.json", json.load)
        
        # set up
        yield app, socketio
        # clean up

    @pytest.fixture()
    def app_client(self, app_socketio: tuple[Flask, SocketIO]) -> FlaskClient:
        app, _ = app_socketio
        return app.test_client()

    @pytest.fixture()
    def socketio_client(
            self,
            app_socketio: tuple[Flask, SocketIO],
            app_client: FlaskClient) -> SocketIOTestClient:
        app, socketio = app_socketio
        return socketio.test_client(app, flask_test_client=app_client)

    @patch('microservice_websocket_docker.app.MOBIUS_URL', "")
    def test_publish_route_post(
            self,
            app_client,
            sensorData_Uplink,
            sensorData_noUplink):

        response: TestResponse = app_client.post("/publish", json=sensorData_Uplink)
        decoded_json: dict = json.loads(response.data)
        payload: dict = websocket_app.to_mobius_payload(sensorData_Uplink)

        print("[DEBUG] Original data: ")
        print(payload)
        print("===========================")
        print("[DEBUG] Data received back from post request: ")
        print(decoded_json)
        assert decoded_json == payload, \
        "Output mismatch when posting valida data. Check stdout log."

        response: TestResponse = app_client.post("/publish", json=sensorData_noUplink)
        decoded_json: dict = json.loads(response.data)
        assert not decoded_json, \
        "Wrong response from post request: should be empty, but it's not"

    @patch('microservice_websocket_docker.app.MOBIUS_URL', "")
    def test_main_route_post(self, app_client: FlaskClient, sensorData_Uplink):
        
        body = {
            "paths": [sensorData_Uplink["tags"]["sensor_path"]],
        }

        response: TestResponse = app_client.post("/", json=body)
        decoded_json: dict = json.loads(response.data)
        assert "data" in decoded_json, "Invalid json from '/' route"
        devices: list = decoded_json["data"]
        assert len(devices) == len(body["paths"]), \
        "Invalid number of devices in json from '/' route"

    @patch('microservice_websocket_docker.app.MOBIUS_URL', "")
    def test_socketio_emits_on_change(
            self,
            app_client: FlaskClient,
            socketio_client: SocketIOTestClient,
            sensorData_Uplink: dict):
        app_client.post("/publish", json=sensorData_Uplink)
        received: list = socketio_client.get_received()
        assert received[0]['name'] == 'change', \
        "Invalid response from socket 'onChange()'"
    
    @patch('microservice_websocket_docker.app.MOBIUS_URL', "")
    def test_get_data(self):
        s: dict = websocket_app.get_data("", "")
        print(f"{s=}")
        assert all(key in s for key in [
                "devEUI",
                "applicationID",
                "state",
                "datiInterni"
            ]) and len(s["datiInterni"]) == 3, \
        "Invalid structure of returned json: doesn't match `to_irma_ui_data()` \
        function, in `data_conversion.py`. Check stdout log."

def _test_update_state_case(current: SensorState, typ: PayloadType,
                           dato: int, expected: SensorState):

    assert websocket_app.update_state(current, typ, dato) == expected, \
    f"Error from state '{current}' with typ '{typ}' and dato '{dato}'. Expected {expected}\
     but got {websocket_app.update_state(current, typ, dato)}"

def test_get_state():
    # From error
    _test_update_state_case(SensorState.ERROR, PayloadType.READING, 0, SensorState.ERROR)
    _test_update_state_case(SensorState.ERROR, PayloadType.READING, MAX_TRESHOLD, SensorState.ERROR)
    _test_update_state_case(SensorState.ERROR, PayloadType.START_REC, 0, SensorState.ERROR)
    _test_update_state_case(SensorState.ERROR, PayloadType.END_REC, 0, SensorState.ERROR)
    _test_update_state_case(SensorState.ERROR, PayloadType.KEEP_ALIVE, 0, SensorState.READY)
    _test_update_state_case(SensorState.ERROR, PayloadType.CONFIRM, 0, SensorState.ERROR)

    # From ready
    _test_update_state_case(SensorState.READY, PayloadType.READING, 0, SensorState.READY)
    _test_update_state_case(SensorState.READY, PayloadType.READING, MAX_TRESHOLD, SensorState.ALERT_READY)
    _test_update_state_case(SensorState.READY, PayloadType.START_REC, 0, SensorState.RUNNING)
    _test_update_state_case(SensorState.READY, PayloadType.END_REC, 0, SensorState.READY)
    _test_update_state_case(SensorState.READY, PayloadType.KEEP_ALIVE, 0, SensorState.READY)
    _test_update_state_case(SensorState.READY, PayloadType.CONFIRM, 0, SensorState.READY)

    # From running
    _test_update_state_case(SensorState.RUNNING, PayloadType.READING, 0, SensorState.RUNNING)
    _test_update_state_case(SensorState.RUNNING, PayloadType.READING, MAX_TRESHOLD, SensorState.ALERT_RUNNING)
    _test_update_state_case(SensorState.RUNNING, PayloadType.START_REC, 0, SensorState.RUNNING)
    _test_update_state_case(SensorState.RUNNING, PayloadType.END_REC, 0, SensorState.READY)
    _test_update_state_case(SensorState.RUNNING, PayloadType.KEEP_ALIVE, 0, SensorState.RUNNING)
    _test_update_state_case(SensorState.RUNNING, PayloadType.CONFIRM, 0, SensorState.RUNNING)

    # From alert_ready
    _test_update_state_case(SensorState.ALERT_READY, PayloadType.READING, 0, SensorState.ALERT_READY)
    _test_update_state_case(SensorState.ALERT_READY, PayloadType.START_REC, 0, SensorState.ALERT_READY)
    _test_update_state_case(SensorState.ALERT_READY, PayloadType.END_REC, 0, SensorState.ALERT_READY)
    _test_update_state_case(SensorState.ALERT_READY, PayloadType.KEEP_ALIVE, 0, SensorState.ALERT_READY)
    _test_update_state_case(SensorState.ALERT_READY, PayloadType.CONFIRM, 0, SensorState.READY)

    # From alert_running
    _test_update_state_case(SensorState.ALERT_RUNNING, PayloadType.READING, 0, SensorState.ALERT_RUNNING)
    _test_update_state_case(SensorState.ALERT_RUNNING, PayloadType.START_REC, 0, SensorState.ALERT_RUNNING)
    _test_update_state_case(SensorState.ALERT_RUNNING, PayloadType.END_REC, 0, SensorState.ALERT_READY)
    _test_update_state_case(SensorState.ALERT_RUNNING, PayloadType.KEEP_ALIVE, 0, SensorState.ALERT_RUNNING)
    _test_update_state_case(SensorState.ALERT_RUNNING, PayloadType.CONFIRM, 0, SensorState.RUNNING)


def test_to_irma_ui():
    sensorID = "2288300834"
    sensorName = "123"
    state = 1
    titolo1 = "Foo"
    titolo2 = "Bar"
    titolo3 = "Baz"
    dato1 = 0.0
    dato2 = 0.0
    dato3 = 0

    expected_value = {
        "sensorID": sensorID,
        "sensorName": sensorName,
        "state": state,
        "datiInterni": [
            {
                "titolo": titolo1,
                "dato": dato1
            },
            {
                "titolo": titolo2,
                "dato": dato2
            },
            {
                "titolo": titolo3,
                "dato": dato3
            }
        ]
    }

    assert websocket_app.to_irma_ui_data(
        sensorID, sensorName, state, 
        titolo1, titolo2, titolo3,
        dato1, dato2, dato3
    ) == expected_value, "Error in `to_irma_ui_data`: output mismatch"



