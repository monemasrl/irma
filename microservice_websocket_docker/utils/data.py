import base64


def decode_data(encoded_data: str) -> dict:
    raw_bytes = base64.b64decode(encoded_data)

    return {
        "payloadType": int.from_bytes(raw_bytes[:1], "big"),
        "sensorData": int.from_bytes(raw_bytes[1:5], "big"),
        "mobius_sensorId": raw_bytes[5:15].decode().strip(),
        "mobius_sensorPath": raw_bytes[15:].decode().strip(),
    }


def encode_mqtt_data(command: int, iso_timestamp: str) -> bytes:
    encoded_data = b""
    encoded_data += command.to_bytes(1, "big")
    encoded_data += iso_timestamp.encode()

    return base64.b64encode(encoded_data)


def to_dashboard_data(
    sensorID: str,
    sensorName: str,
    applicationID: str,
    state: str,
    titolo1: str,
    titolo2: str,
    titolo3: str,
    dato1: float,
    dato2: float,
    dato3: int,
    unhandledAlertIDs: list,
) -> dict:

    return {
        "sensorID": sensorID,
        "sensorName": sensorName,
        "applicationID": applicationID,
        "state": state,
        "datiInterni": [
            {"titolo": titolo1, "dato": dato1},
            {"titolo": titolo2, "dato": dato2},
            {"titolo": titolo3, "dato": dato3},
        ],
        "unhandledAlertIDs": unhandledAlertIDs,
    }
