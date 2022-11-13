from datetime import datetime

from .. import mqtt
from ..config import config
from ..services.database import Alert, Application, Node, Reading
from .enums import NodeState, PayloadType
from .exceptions import ObjectNotFoundException
from .node import update_state
from .sync_cache import add_to_cache

DISABLE_MQTT = False


def publish(record: dict) -> dict:

    applicationID: str = record["applicationID"]
    nodeID: str = record["nodeID"]

    application = Application.objects(id=applicationID).first()

    if application is None:
        raise ObjectNotFoundException(Application)

    node = Node.objects(nodeID=nodeID).first()

    if node is None:
        node = Node(
            nodeID=nodeID,
            application=application,
            organization=application["organization"],
            nodeName=record["nodeName"],
            state=NodeState.READY,
            lastSeenAt=datetime.now(),
        )
        node.save()

    if record["payloadType"] == PayloadType.TOTAL_READING:
        handle_total_reading(node, record)

    elif record["payloadType"] == PayloadType.WINDOW_READING:
        handle_window_reading(node, record)

    value = record["data"].get("value", 0)

    node["lastSeenAt"] = datetime.now()
    node["state"] = update_state(
        node["state"],
        node["lastSeenAt"],
        record["payloadType"],
        value,
    )
    node.save()

    return record


def handle_total_reading(node: Node, record: dict):
    reading = Reading.objects(
        nodeID=node["nodeID"],
        readingID=record["data"]["readingID"],
        canID=record["data"]["canID"],
        sensorNumber=record["data"]["sensorNumber"],
    ).first()

    if reading is None:
        reading = Reading(
            nodeID=node["nodeID"],
            canID=record["data"]["canID"],
            sensorNumber=record["data"]["sensorNumber"],
            readingID=record["data"]["readingID"],
            sessionID=record["data"]["sessionID"],
            publishedAt=datetime.now(),
        )

    reading["dangerLevel"] = record["data"]["value"]
    reading.save()
    add_to_cache(str(reading["id"]))

    if reading["dangerLevel"] >= config["ALERT_TRESHOLD"]:
        alert = Alert.objects(sessionID=reading["sessionID"], isHandled=False).first()

        if alert is None:
            alert = Alert(
                reading=reading,
                node=node,
                sessionID=reading["sessionID"],
                isHandled=False,
                raisedAt=datetime.now(),
            )
            alert.save()


def handle_window_reading(node: Node, record: dict):
    reading = Reading.objects(
        nodeID=node["nodeID"],
        readingID=record["data"]["readingID"],
        canID=record["data"]["canID"],
        sensorNumber=record["data"]["sensorNumber"],
    ).first()

    if reading is None:
        reading = Reading(
            nodeID=node["nodeID"],
            canID=record["data"]["canID"],
            sensorNumber=record["data"]["sensorNumber"],
            sessionID=record["data"]["sessionID"],
            readingID=record["data"]["readingID"],
            publishedAt=datetime.now(),
        )

    window_number = record["data"]["value"]

    if window_number == 0:
        reading["window1_count"] = record["data"]["count"]
    elif window_number == 1:
        reading["window2_count"] = record["data"]["count"]
    elif window_number == 2:
        reading["window3_count"] = record["data"]["count"]
    else:
        raise ValueError(f"Unexpected window_number: {window_number}")

    reading.save()
    add_to_cache(str(reading["id"]))


def send_mqtt_command(applicationID: str, nodeID: str, command: int):
    topic: str = f"{applicationID}/{nodeID}/command"

    data: bytes = command.to_bytes(1, "big")

    if not DISABLE_MQTT:
        mqtt.publish(topic, data)
