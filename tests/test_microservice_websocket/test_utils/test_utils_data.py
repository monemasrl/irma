from microservice_websocket.app.utils.data import decode_data, encode_mqtt_data


def test_decode_data():
    encoded_data: str = "AQEBAw9CQAAZfaAAGX22"

    expected_output = {
        "payloadType": 1,
        "canID": 1,
        "sensorNumber": 1,
        "value": 3,
        "count": 1_000_000,
        "sessionID": 1_670_560,
        "readingID": 1_670_582,
    }

    assert (
        decode_data(encoded_data) == expected_output
    ), "Error in `decode_data`: output mismatch"


def test_encode_mqtt_data():
    command: int = 1

    expected_output: bytes = b"AQ=="

    assert (
        encode_mqtt_data(command) == expected_output
    ), "Error in `encode_mqtt_data`: output mismatch"
