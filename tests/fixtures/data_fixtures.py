"""
Data fixtures based on chirpstack data
"""

import pytest
from mockHttp.microservice_websocket import decode_devEUI, State


@pytest.fixture()
def sensorId() -> str:
    """
    Basic applicationID received from chirpstack.
    It's a string composed of a sequence of numbers.
    """
    return "123"


@pytest.fixture()
def readingTimestamp() -> str:
    """
    Time format received from chirpstack.
    It does follow the ISO8601 standard.
    """
    return "2013-03-31T16:21:17.528002Z"


@pytest.fixture()
def latitude() -> float:
    """
    Example of latitude received from chirpstack.
    It's a generic floating point number.
    """
    return 45.7


@pytest.fixture()
def longitude() -> float:
    """
    Example of longitude received from chirpstack.
    It's a generic floating point number.
    """
    return 34.8


@pytest.fixture()
def devEUI() -> str:
    """
    Example of devEUI received from chirpstack, NOT decoded
    """
    return "AgICAgICAgI="


@pytest.fixture()
def decoded_devEUI(devEUI) -> str:
    """
    Example of devEUI decoded from `decode_devEUI()`
    """
    return decode_devEUI(devEUI)


@pytest.fixture()
def state() -> str:
    """
    Example of state from the State class inside `microservice_websocket.py`
    """
    return State.OK.name


@pytest.fixture()
def sensorData_noUplink(sensorId, readingTimestamp,
                        latitude, longitude, devEUI) -> dict:
    return {
        "applicationID": sensorId,
        "applicationName": "temperature-sensor",
        "deviceName": "garden-sensor",
        "devEUI": devEUI,
        "rxInfo": [
            {
                "gatewayID": "AwMDAwMDAwM=",
                "time": readingTimestamp,
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

@pytest.fixture()
def sensorData_Uplink(sensorId, readingTimestamp, latitude, longitude) -> dict:
    return {
        "applicationID": sensorId,
        "applicationName": "test_esp",
        "deviceName": "esp32",
        "devEUI": "IjIzAACIiAI=",
        "rxInfo": [
            {
                "gatewayID": "5F8B//59p6g=",
                "time": readingTimestamp,
                "timeSinceGPSEpoch": None,
                "rssi": -10,
                "loRaSNR": 8.5,
                "channel": 4,
                "rfChain": 0,
                "board": 0,
                "antenna": 0,
                "location": {
                    "latitude": latitude,
                    "longitude": longitude,
                    "altitude": 0,
                    "source": "UNKNOWN",
                    "accuracy": 0
                },
                "fineTimestampType": "NONE",
                "context": "Ki0a3A==",
                "uplinkID": "wPR+sie0RG2x6bz5t4+G3Q==",
                "crcStatus": "CRC_OK"
            }
        ],
        "txInfo": {
            "frequency": 867300000,
            "modulation": "LORA",
            "loRaModulationInfo": {
                "bandwidth": 125,
                "spreadingFactor": 12,
                "codeRate": "4/5",
                "polarizationInversion": False
            }
        },
        "adr": True,
        "dr": 0,
        "fCnt": 579,
        "fPort": 2,
        "data": "AAE=",
        "objectJSON": "{\"sensorData\":1}",
        "tags": {},
        "confirmedUplink": True,
        "devAddr": "AS6zcQ==",
        "publishedAt": "2022-06-23T13:32:08.564170948Z",
        "deviceProfileID": "fc9a26f4-58fe-47b0-bfe9-2cb7711f1de1",
        "deviceProfileName": "testOTAA"
    }
