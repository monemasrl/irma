from mockHttp import microservice_websocket
import pytest

@pytest.fixture()
def iD():
    return "123"

@pytest.fixture()
def time():
    return "2013-03-31T16:21:17.528002Z"

@pytest.fixture()
def latitude():
    return 45.7

@pytest.fixture()
def longitude():
    return 34.8

@pytest.fixture()
def sensorData(iD, time, latitude, longitude):
    return {
        "applicationID": iD,
        "applicationName": "temperature-sensor",
        "deviceName": "garden-sensor",
        "devEUI": "AgICAgICAgI=",
        "rxInfo": [
            {
                "gatewayID": "AwMDAwMDAwM=",
                "time": time,
                "timeSinceGPSEpoch": None,
                "rssi": -48,
                "loRaSNR": 9,
                "channel": 5,
                "rfChain": 0,
                "board": 0,
                "antenna": 0,
                "location": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "altitude": 10.5
                },
                "fineTimestampType": "NONE",
                "context": "9u/uvA==",
                "uplinkID": "jhMh8Gq6RAOChSKbi83RHQ=="
            }
        ],
        "txInfo": {
            "frequency": 868100000,
            "modulation": "LORA",
            "loRaModulationInfo": {
                "bandwidth": 125,
                "spreadingFactor": 11,
                "codeRate": "4/5",
                "polarizationInversion": False
            }
        },
        "adr": True,
        "dr": 1,
        "fCnt": 10,
        "fPort": 5,
        "data": "...",
        "objectJSON": "{\"temperatureSensor\":25,\"humiditySensor\":32}",
        "tags": {
            "key": "value"
        }
    }


class TestDBDocs:

    # def setup_method(self):
    #     self.app = microservice_websocket.app
    #     self.app.config['TESTING'] = True
    #     self.app.test_client()

    @pytest.fixture()
    def payload(self, iD, time, latitude, longitude, sensorData):
        return microservice_websocket.Payload(
            iD=iD,
            time=time,
            latitude=latitude,
            longitude=longitude,
            sensorData=sensorData,
        )
        
    def test_Payload_to_json(self, payload):
        payload_dict = {
            "m2m:cin": {
                "con": {
                    "metadata": {
                        "sensorId": payload.iD,
                        "readingTimestamp": payload.time,
                        "latitude": payload.latitude,
                        "longitude": payload.longitude,
                    }
                },
                "sensorData": payload.sensorData,
            }
        }

        assert payload.to_json() == payload_dict, "Error in `Payload.to_json`: output mismatch"

    def test_SentDocument_to_jsonSent(self):
        sentDocument = microservice_websocket.SentDocument(
            eui=123,
            status="rec",
            code=456,
            titolo1="Titolo 1",
            dato1=7.89,
            titolo2="",
            dato2=-2,
            titolo3="Titolo 3!",
            dato3=-3j
        )

        sentDocument_dict = {
            "devEUI": 123,
            "state": "rec",
            "code": 456,
            "datiInterni": [
                {
                    "titolo": "Titolo 1",
                    "dato": 7.89
                },
                {
                    "titolo": "",
                    "dato": -2
                },
                {
                    "titolo": "Titolo 3!",
                    "dato": -3j
                }
            ]
        }

        assert sentDocument.to_jsonSent() == sentDocument_dict, "Error in `SentDocument.to_jsonSent()`: output mismatch"


class TestFlaskApp:

    @pytest.fixture()
    def app(self, payload: microservice_websocket.Payload):
        app = microservice_websocket.app
        app.config.update({
            "TESTING": True,
        })
        app.config['MONGODB_CONNECT'] = False
        # set up
        yield app
        # clean up
 
    @pytest.fixture()
    def client(self, app):
        return app.test_client()

    def test_main_route_get(self, client):
        assert False
        response = client.get("/")
        print(response.data)
        assert False


def test_prepareData():
    data = """{"sensorData": 123}"""

    assert microservice_websocket.prepareData(data) == 123, "Error in `prepareData()`: output mismatch"


def test_mSum_rightMonth():
    assert microservice_websocket.mSum(10, 4, 4) == 10, "Error in `mSum(): output mismatch"


def test_mSum_wrongMonth():
    assert microservice_websocket.mSum(10, 4, 7) == 0, "Error in `mSum(): output mismatch"


def test_prepare_status_off():
    dato = 0
    assert microservice_websocket.prepare_status(dato) == "off", "Error in `prepare_status()` with dato = 0: output mismatch"


def test_prepare_status_ok():
    dato = microservice_websocket.MAX_TRESHOLD-1
    assert microservice_websocket.prepare_status(dato) == "ok", "Error in `prepare_status()` with dato < MAX_TRESHOLD: output mismatch"


def test_prepare_status_alert():
    dato = microservice_websocket.MAX_TRESHOLD+1
    assert microservice_websocket.prepare_status(dato) == "alert", "Error in `prepare_status()` with dato >= MAX_TRESHOLD: output mismatch"


def test_prepare_status_invalid_input():
    dato = "foo"
    with pytest.raises(TypeError):
        microservice_websocket.prepare_status(dato)


def test_prepare_month_ok(time):
    assert microservice_websocket.prepare_month(time) == 3, "Error in `prepare_month()`: output mismatch"


def test_prepare_month_error():
    with pytest.raises(ValueError):
        microservice_websocket.prepare_month("1-0")


def test_prepareData_ok():
    data = '{"sensorData": 123}'
    assert microservice_websocket.prepareData(data) == 123, "Error in `prepareData()`: output mismatch"


def test_prepareData_invalid_value():
    data = '{"sensorData": 1-0}'
    with pytest.raises(ValueError):
        microservice_websocket.prepareData(data)


def test_prepareData_absent_key():
    data = '{"foo": "bar"}'
    with pytest.raises(KeyError):
        microservice_websocket.prepareData(data)


def test_getData():
    pass # TODO!

