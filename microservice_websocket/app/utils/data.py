import base64


def decode_data(encoded_data: str) -> dict:
    raw_bytes = base64.b64decode(encoded_data)

    return {
        "payloadType": int.from_bytes(raw_bytes[:1], "big"),
        "canID": int.from_bytes(raw_bytes[1:2], "big"),
        "sensorNumber": int.from_bytes(raw_bytes[2:3], "big"),
        "dangerLevel": int.from_bytes(raw_bytes[3:4], "big"),
        "window1_count": int.from_bytes(raw_bytes[4:5], "big"),
        "window2_count": int.from_bytes(raw_bytes[5:6], "big"),
        "window3_count": int.from_bytes(raw_bytes[6:7], "big"),
        "sessionID": int.from_bytes(raw_bytes[7:8], "big"),
    }


def encode_mqtt_data(command: int, iso_timestamp: str) -> bytes:
    encoded_data = b""
    encoded_data += command.to_bytes(1, "big")
    encoded_data += iso_timestamp.encode()

    return base64.b64encode(encoded_data)
