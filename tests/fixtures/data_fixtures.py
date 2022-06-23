"""
Data fixtures based on chirpstack data
"""

import pytest


@pytest.fixture()
def iD() -> str:
    """
    Basic applicationID received from chirpstack.
    It's a string composed of a sequence of numbers.
    """
    return "123"


@pytest.fixture()
def time() -> str:
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
def sensorData_noUplink(iD, time, latitude, longitude) -> dict:
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