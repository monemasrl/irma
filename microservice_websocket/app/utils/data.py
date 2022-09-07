import base64
from datetime import datetime

from ..services import database as db
from .enums import NodeState


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


def fetch_data(sensorID: str) -> dict:
    total_sum: int = 0
    monthly_sum: int = 0

    total_count: int = 0
    monthly_count: int = 0

    total_average: float = 0.0
    monthly_average: float = 0.0

    # salvataggio del valore attuale del mese per il confronto
    current_month: int = datetime.now().month

    sensor = db.Sensor.objects(sensorID=sensorID).first()

    if sensor is None:
        return {}

    state: NodeState = sensor["state"]
    sensorName: str = sensor["sensorName"]
    applicationID: str = str(sensor["application"]["id"])

    collect = db.Reading.objects(sensor=sensor).order_by("-publishedAt")

    unhandledAlerts = db.Alert.objects(sensor=sensor, isHandled=False)

    unhandledAlertIDs = [str(x["id"]) for x in unhandledAlerts]

    for x in collect:
        for data in x["data"]:
            sensor_data: int = data["sensorData"]
            read_time: datetime = data["publishedAt"]
            read_month: int = read_time.month

            total_sum += sensor_data
            total_count += 1

            if read_month == current_month:
                monthly_sum += sensor_data
                monthly_count += 1

            total_average = total_sum / total_count

            if monthly_count != 0:
                monthly_average = monthly_sum / monthly_count

    send: dict = to_dashboard_data(
        sensorID=sensorID,
        sensorName=sensorName,
        applicationID=applicationID,
        state=NodeState.to_irma_ui_state(state),
        titolo1="Media Letture Totali",
        dato1=round(total_average, 3),
        titolo2="Media Letture Mensili",
        dato2=round(monthly_average, 3),
        titolo3="Letture eseguite nel mese",
        dato3=monthly_count,
        unhandledAlertIDs=unhandledAlertIDs,
    )

    return send
