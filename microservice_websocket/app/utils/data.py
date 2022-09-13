import base64


def decode_data(encoded_data: str) -> dict:
    raw_bytes = base64.b64decode(encoded_data)

    return {
        "payloadType": int.from_bytes(raw_bytes[:1], "big"),
        "canID": int.from_bytes(raw_bytes[1:2], "big"),
        "sensorNumber": int.from_bytes(raw_bytes[2:3], "big"),
        "value": int.from_bytes(raw_bytes[3:4], "big"),
        "count": int.from_bytes(raw_bytes[4:7], "big"),
        "sessionID": int.from_bytes(raw_bytes[7:11], "big"),
        "readingID": int.from_bytes(raw_bytes[11:15], "big"),
    }


def encode_mqtt_data(command: int) -> bytes:
    encoded_data = b""
    encoded_data += command.to_bytes(1, "big")

    return base64.b64encode(encoded_data)
