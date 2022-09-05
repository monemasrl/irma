import json

import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_socketio import SocketIO, SocketIOTestClient
from mock import patch

import microservice_websocket.app as websocket_app


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
