"""
Data fixtures based on chirpstack data
"""

import pytest


@pytest.fixture()
def sensorId() -> str:
    """
    sensorId defined in the tags section of the sensor
    """
    return "FOO_bar_01"


@pytest.fixture()
def applicationID() -> str:
    """
    applicationID which identifies the application running on chirpstackself.
    It's a string containing a number
    """
    return "1"


@pytest.fixture()
def isoTimestamp() -> str:
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
def sensorData_noUplink(sensorId, applicationID, isoTimestamp,
                        latitude, longitude, devEUI) -> dict:
    return {
        "applicationID": applicationID,
        "applicationName": "temperature-sensor",
        "deviceName": "garden-sensor",
        "devEUI": devEUI,
        "rxInfo": [
            {
                "gatewayID": "AwMDAwMDAwM=",
                "time": isoTimestamp,
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
            "sensorId": sensorId,
            "sensor_path": "433423432"
        }
    }

@pytest.fixture()
def sensorData_Uplink(devEUI, applicationID, sensorId, isoTimestamp, latitude, longitude) -> dict:
    return {
        "applicationID": applicationID,
        "applicationName": "irma",
        "deviceName": "irma-sensor",
        "devEUI": devEUI,
        "rxInfo": [
            {
                "gatewayID": "e45f01fffe7da7a8",
                "time": None,
                "timeSinceGPSEpoch": None,
                "rssi": -61,
                "loRaSNR": -2.8,
                "channel": 7,
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
                "context": "XZ4gbA==",
                "uplinkID": "76d9f46d-d799-491e-ac16-48f953077232",
                "crcStatus": "CRC_OK"
            }
        ],
        "txInfo": {
            "frequency": 867900000,
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
        "fCnt": 6,
        "fPort": 2,
        "data": "ABE=",
        "objectJSON": {
            "sensorData": 17
        },
        "tags": {
            "sensorId": sensorId,
            "sensor_path": "283923423"
        },
        "confirmedUplink": True,
        "devAddr": "0021051c",
        "publishedAt": isoTimestamp,
        "deviceProfileID": "be018f1b-c068-43c0-a276-a7665ff090b4",
        "deviceProfileName": "device-OTAA"
    }


def node_data() -> dict:
    return {
        "sensorID": 1,
        "applicationID": "foo",
        "organizationID": "bar",
        # "deviceName": "irma-sensor",
        "data": {
            "state": 3,
            "sensorData": 4.5,
            "mobius_sensorId": "foo",
            "mobius_sensorPath": "bar",
        },
        "publishedAt": "time",
        "payloadType": 1
    }

