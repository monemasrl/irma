import os
from datetime import datetime

from .. import mqtt
from ..services.database import Alert, Application, Node, Reading
from .enums import NodeState, PayloadType
from .exceptions import ObjectNotFoundException
from .node import MAX_TRESHOLD, update_state

# mobius url
# TODO: move to config file
MOBIUS_URL = os.environ.get("MOBIUS_URL", "http://localhost")
MOBIUS_PORT = os.environ.get("MOBIUS_PORT", "5002")

# for testing purposes
# TODO: move to config file and merge with app.py
DISABLE_MQTT = False if os.environ.get("DISABLE_MQTT") != 1 else True


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
    # TODO: reimplememnt
    # if MOBIUS_URL != "":
    #     insert(record)

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
            publishedAt=datetime.now().isoformat(),
        )

    reading["dangerLevel"] = record["data"]["value"]
    reading.save()

    if reading["dangerLevel"] >= MAX_TRESHOLD:
        alert = Alert.objects(sessionID=reading["sessionID"], isHandled=False).first()

        if alert is None:
            alert = Alert(
                reading=reading,
                node=node,
                sessionID=reading["sessionID"],
                isHandled=False,
            )
            alert.save()


def handle_window_reading(node: Node, record: dict):
    # TODO: reimplememnt
    # if MOBIUS_URL != "":
    #     insert(record)

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
            publishedAt=datetime.now().isoformat(),
        )

    window_number = record["data"]["value"]

    if window_number == 1:
        reading["window1_count"] = record["data"]["count"]
    elif window_number == 2:
        reading["window2_count"] = record["data"]["count"]
    elif window_number == 3:
        reading["window3_count"] = record["data"]["count"]
    else:
        raise ValueError(f"Unexpected window_number: {window_number}")

    reading.save()


def send_mqtt_command(applicationID: str, nodeID: str, command: int):
    topic: str = f"{applicationID}/{nodeID}/command"

    data: bytes = command.to_bytes(1, "big")

    if not DISABLE_MQTT:
        mqtt.publish(topic, data)
