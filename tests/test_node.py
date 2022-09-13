from node import app
from node.can_protocol import DecodedMessage


def test_encode_data():
    payload_type: int = 1
    data: DecodedMessage = {
        "n_detector": 1,
        "sipm": 1,
        "value": 3,
        "count": 1_000_000,
        "sessionID": 1_670_560,
        "readingID": 1_670_582,
    }

    expected_output: str = "AQEBAw9CQAAZfaAAGX22"

    assert (
        app.encode_data(
            payload_type=payload_type,
            data=data,
        )
        == expected_output
    ), "Error in `encode_data`: output mismatch"


def test_decode_mqtt_data():
    encoded_string: str = "AQ=="

    expected_output = {"command": 1}

    assert (
        app.decode_mqtt_data(encoded_string) == expected_output
    ), "Error in `decode_mqtt_data`: output mismatch"
