from mockHttp import microservice_websocket, microservice_db
import pytest
import json
import base64
from fixtures.data_fixtures import *


class TestFlaskApp:

    @pytest.fixture()
    def app(self):
        app, _ = microservice_websocket.create_app()
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
        yield app
        # clean up
 
    @pytest.fixture()
    def client(self, app):
        return app.test_client()

    def test_main_route_get(self, client):
        response = client.get("/")
        decoded_json = json.loads(response.data)
        assert "data" in decoded_json, "Invalid json from '/' route"
        devices = decoded_json["data"]
        assert len(devices) == microservice_websocket.N_DEVICES, "Invalid number of devices in json from '/' route"

    def test_main_route_post_Uplink(self, client, sensorData_Uplink, sensorData_noUplink):
        response = client.post("/", json=sensorData_Uplink)
        decoded_json = json.loads(response.data)
        sensorData_Uplink['devEUI']=base64.b64decode(sensorData_Uplink['devEUI']).hex()
        payload = microservice_db.Payload(
            iD=sensorData_Uplink['applicationID'],
            time=sensorData_Uplink['publishedAt'],
            latitude=sensorData_Uplink['rxInfo'][0]['location']['latitude'],
            longitude=sensorData_Uplink['rxInfo'][0]['location']['longitude'],
            sensorData=sensorData_Uplink
        )
        assert decoded_json == payload.to_json(), "Output mismatch when posting valida data"

        response = client.post("/", json=sensorData_noUplink)
        decoded_json = json.loads(response.data)
        assert not decoded_json, "Wrong response from post request: should be empty, but it's not"


def test_mSum():
    assert microservice_websocket.mSum(10, 4, 4) == 10, "Error in `mSum(): output mismatch with right month"
    assert microservice_websocket.mSum(10, 4, 7) == 0, "Error in `mSum(): output mismatch with different month"


def test_prepare_status():
    dato = 0
    assert microservice_websocket.prepare_status(dato) == "off", "Error in `prepare_status()` with dato == 0: output mismatch"

    dato = microservice_websocket.MAX_TRESHOLD-1
    assert microservice_websocket.prepare_status(dato) == "ok", "Error in `prepare_status()` with dato < MAX_TRESHOLD: output mismatch"

    dato = microservice_websocket.MAX_TRESHOLD+1
    assert microservice_websocket.prepare_status(dato) == "alert", "Error in `prepare_status()` with dato >= MAX_TRESHOLD: output mismatch"

    dato = "foo"
    with pytest.raises(TypeError):
        microservice_websocket.prepare_status(dato)


def test_prepare_month(time):
    assert microservice_websocket.prepare_month(time) == 3, "Error in `prepare_month()`: output mismatch when providin ISO8601 datetime"

    with pytest.raises(ValueError):
        microservice_websocket.prepare_month("1-0")


def test_prepareData():
    data = '{"sensorData": 123}'
    assert microservice_websocket.prepareData(data) == 123, "Error in `prepareData()`: output mismatch when providing right input"

    data = '{"sensorData": 1-0}'
    with pytest.raises(ValueError):
        microservice_websocket.prepareData(data)

    data = '{"foo": "bar"}'
    with pytest.raises(KeyError):
        microservice_websocket.prepareData(data)


def test_getData():
    pass # TODO:!
