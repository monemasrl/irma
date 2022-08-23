from node import app


def test_encode_data():
    payload_type: int = 1
    data: int = 7
    mobius_sensorId: str = "mobiusId"
    mobius_sensorPath: str = "mobiusPath"

    expected_output: str = "AQAAAAdtb2JpdXNJZCAgbW9iaXVzUGF0aA=="

    assert app.encode_data(
        payload_type=payload_type,
        data=data,
        mobius_sensorId=mobius_sensorId,
        mobius_sensorPath=mobius_sensorPath
    ) == expected_output, "Error in `encode_data`: output mismatch"


def test_decode_mqtt_data():
    encoded_string: str = "ATIwMjItMDgtMjNUMTE6MDY6MDAuNjc2NDk3"

    expected_output = {
        "command": 1,
        "commandTimestamp": "2022-08-23T11:06:00.676497"
    }

    assert app.decode_mqtt_data(encoded_string) == expected_output, \
    "Error in `decode_mqtt_data`: output mismatch"
