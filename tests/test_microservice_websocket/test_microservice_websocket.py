from unittest.mock import mock_open

import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_socketio import SocketIO, SocketIOTestClient
from mock import patch

from microservice_websocket.app import create_app, socketio
from tests.test_microservice_websocket.test_routes import test_bp


class TestFlaskApp:
    @pytest.fixture()
    def testing_app(self) -> Flask:
        with patch("microservice_websocket.app.DISABLE_MQTT", True):
            app = create_app(testing=True)

        app.register_blueprint(test_bp)

        # set up
        yield app
        # clean up

    @pytest.fixture()
    def testing_socketio(self) -> SocketIO:
        return socketio

    @pytest.fixture()
    def app_client(self, testing_app: Flask) -> FlaskClient:
        return testing_app.test_client()

    @pytest.fixture()
    def socketio_client(
        self, testing_app: Flask, app_client: FlaskClient, testing_socketio: SocketIO
    ) -> SocketIOTestClient:
        return socketio.test_client(testing_app, flask_test_client=app_client)

    def test_api_token_decorator(self, app_client: FlaskClient):
        test_url = "http://localhost:5000/test/api-token-test"

        response = app_client.get(test_url)

        assert (
            response.status_code == 401
        ), "Invalid response code from route protected with @api_token_required"

        with patch("builtins.open", mock_open(read_data="1234")):
            response = app_client.get(
                test_url, headers={"Authorization": "Bearer 1234"}
            )

        assert (
            response.status_code == 200
        ), "Cannot access route protected with @api_token_required with correct api-token"

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
