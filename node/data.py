import base64

from can_protocol import DecodedMessage


def encode_data(
    payload_type: int,
    data: DecodedMessage,
) -> str:

    byts = b""
    byts += payload_type.to_bytes(1, "big")

    if data is not None:
        byts += data["n_detector"].to_bytes(1, "big")
        byts += data["sipm"].to_bytes(1, "big")
        byts += data["value"].to_bytes(1, "big")
        byts += data["count"].to_bytes(3, "big")
        byts += data["sessionID"].to_bytes(4, "big")
        byts += data["readingID"].to_bytes(4, "big")
    else:
        byts += b"0" * 14

    return base64.b64encode(byts).decode()


def decode_mqtt_data(encoded_string: str) -> dict:
    encoded_data = base64.b64decode(encoded_string)
    return {
        "command": int.from_bytes(encoded_data[:1], "big"),
    }
