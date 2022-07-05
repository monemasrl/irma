from flask_socketio import SocketIO, SocketIOTestClient
from flask import Flask
from flask.testing import FlaskClient
from werkzeug.test import TestResponse
from hypothesis import given
from hypothesis.strategies import text
from mockHttp import microservice_websocket, microservice_db
import pytest
import json
import base64
from fixtures.data_fixtures import *


class TestFlaskApp:

    @pytest.fixture()
    def app_socketio(self) -> tuple[Flask, SocketIO]: # type: ignore
        app, socketio = microservice_websocket.create_app()
        app.config.update({
            "TESTING": True,
        })
        app.config['MONGODB_CONNECT'] = False
        app.config['MONGODB_SETTINGS'] = {
            'db': 'mongoenginetest',
            'host': 'mongomock://localhost',
            'port': 27017
        }
        db = microservice_websocket.init_db(app)
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

    def test_main_route_get(self, app_client: FlaskClient):
        response: TestResponse = app_client.get("/")
        decoded_json: dict = json.loads(response.data)
        assert "data" in decoded_json, "Invalid json from '/' route"
        devices: list = decoded_json["data"]
        assert len(devices) == microservice_websocket.N_DEVICES, \
        "Invalid number of devices in json from '/' route"

    def test_main_route_post_Uplink(
            self,
            app_client,
            sensorData_Uplink,
            sensorData_noUplink):
        response: TestResponse = app_client.post("/", json=sensorData_Uplink)
        decoded_json: dict = json.loads(response.data)
        sensorData_Uplink['devEUI'] = base64.b64decode(sensorData_Uplink['devEUI']).hex()
        payload: microservice_db.Payload = microservice_db.Payload(
            sensorId=sensorData_Uplink['applicationID'],
            readingTimestamp=sensorData_Uplink['publishedAt'],
            latitude=sensorData_Uplink['rxInfo'][0]['location']['latitude'],
            longitude=sensorData_Uplink['rxInfo'][0]['location']['longitude'],
            sensorData=sensorData_Uplink
        )
        print("[DEBUG] Original data: ")
        print(payload.to_json())
        print("===========================")
        print("[DEBUG] Data received back from post request: ")
        print(decoded_json)
        assert decoded_json == payload.to_json(), \
        "Output mismatch when posting valida data. Check stdout log."

        payloads = microservice_db.Payload.objects() # type: ignore
        assert len(payloads) > 0, "Payload not saved in database"
        assert payloads[0].to_json() == payload.to_json(), \
        "Payload inserted with wrong fields in database"

        response: TestResponse = app_client.post("/", json=sensorData_noUplink)
        decoded_json: dict = json.loads(response.data)
        assert not decoded_json, \
        "Wrong response from post request: should be empty, but it's not"

    def test_socketio_emits_on_change(
            self,
            app_client: FlaskClient,
            socketio_client: SocketIOTestClient,
            sensorData_Uplink: dict):
        app_client.post("/", json=sensorData_Uplink)
        received: list = socketio_client.get_received()
        assert received[0]['name'] == 'change', \
        "Invalid response from socket 'onChange()'"
    
    def test_db_holds_payloads(self, sensorData_Uplink: dict):
        """
        This test is meant to check if data stored
        as Payload in database is consistent
        """
        payload: microservice_db.Payload = microservice_db.Payload(
            sensorId=sensorData_Uplink['applicationID'],
            readingTimestamp=sensorData_Uplink['publishedAt'],
            latitude=sensorData_Uplink['rxInfo'][0]['location']['latitude'],
            longitude=sensorData_Uplink['rxInfo'][0]['location']['longitude'],
            sensorData=sensorData_Uplink
        )
        payload.save()
        payloads = microservice_db.Payload.objects() # type: ignore
        assert len(payloads) > 0, "Payloads aren't saved in the database"
        print("[DEBUG] Original payload: ")
        print(payload)
        print("===========================")
        print("[DEBUG] Last inserted payload in the database: ")
        print(payloads[len(payloads)-1])
        assert payload.to_json() == payloads[len(payloads)-1].to_json(), \
        "Payload data isn't consistent in the database. Check stdout log."

    def test_get_data(self):
        s: str = microservice_websocket.get_data("123", "123")
        s_dict: dict = json.loads(s)
        print(f"{s_dict=}")
        assert all(key in s_dict for key in [
                "devEUI",
                "state",
                "code",
                "datiInterni"
            ]) and len(s_dict["datiInterni"]) == 3, \
        "Invalid structure of returned json: doesn't match `to_jsonSent()` \
        function, in `microservice_db.py`. Check stdout log."


def test_decode_devEUI(devEUI):
    assert microservice_websocket.decode_devEUI(devEUI) == "0202020202020202", \
    "Error in `decode_devEUI()`: output mismatch"


def test_get_state():
    dato: int = 0
    assert microservice_websocket.get_state(dato) == microservice_websocket.State.OFF, \
    "Error in `get_state()` with dato == 0: output mismatch"

    dato = microservice_websocket.MAX_TRESHOLD-1
    assert microservice_websocket.get_state(dato) == microservice_websocket.State.OK, \
    "Error in `get_state()` with dato < MAX_TRESHOLD: output mismatch"

    dato = microservice_websocket.MAX_TRESHOLD+1
    assert microservice_websocket.get_state(dato) == microservice_websocket.State.ALERT, \
    "Error in `get_state()` with dato >= MAX_TRESHOLD: output mismatch"


def test_get_month(readingTimestamp):
    assert microservice_websocket.get_month(readingTimestamp) == 3, \
    "Error in `get_month()`: output mismatch when providin ISO8601 datetime"

    with pytest.raises(ValueError):
        microservice_websocket.get_month("1-0")


def test_get_sensorData():
    data: str = '{"sensorData": 123}'
    assert microservice_websocket.get_sensorData(data) == 123, \
    "Error in `get_sensorData()`: output mismatch when providing right input"

    data: str = '{"sensorData": 1-0}'
    with pytest.raises(ValueError):
        microservice_websocket.get_sensorData(data)

    data: str = '{"foo": "bar"}'
    with pytest.raises(KeyError):
        microservice_websocket.get_sensorData(data)


