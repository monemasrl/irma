import os
from datetime import datetime

from .. import mqtt
from ..services.database import Alert, Application, Node, TotalReading, WindowReading
from .data import decode_data, encode_mqtt_data
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
    record["data"] = decode_data(record["data"])

    # Vero se arriva da chirpstack
    if "txInfo" in record:
        # TODO: portare a payload di node/app.py
        pass

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

    if record["data"]["payloadType"] == PayloadType.TOTAL_READING:
        handle_total_reading(node, record)

    if record["data"]["payloadType"] == PayloadType.WINDOW_READING:
        handle_window_reading(node, record)

    node["lastSeenAt"] = datetime.now()
    node["state"] = update_state(
        node["state"],
        node["lastSeenAt"],
        record["data"]["payloadType"],
        record["data"]["value"],
    )
    node.save()

    return record


def handle_total_reading(node: Node, record: dict):
    # TODO: reimplememnt
    # if MOBIUS_URL != "":
    #     insert(record)

    reading = TotalReading(
        nodeID=node["nodeID"],
        canID=record["data"]["canID"],
        sensorNumber=record["data"]["sensorNumber"],
        dangerLevel=record["data"]["value"],
        totalCount=record["data"]["count"],
        sessionID=record["data"]["sessionID"],
        readingID=record["data"]["readingID"],
        publishedAt=datetime.now().isoformat(),
    )

    reading.save()

    if reading["dangerLevel"] >= MAX_TRESHOLD:
        alert = Alert.objects(sessionID=reading["sessionID"]).first()

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

    reading = WindowReading(
        nodeID=node["nodeID"],
        canID=record["data"]["canID"],
        sensorNumber=record["data"]["sensorNumber"],
        window_number=record["data"]["value"],
        count=record["data"]["count"],
        sessionID=record["data"]["sessionID"],
        readingID=record["data"]["readingID"],
        publishedAt=datetime.now().isoformat(),
    )

    reading.save()


def send_mqtt_command(applicationID: str, nodeID: str, command: int):
    topic: str = f"{applicationID}/{nodeID}/command"

    data: bytes = encode_mqtt_data(command)

    if not DISABLE_MQTT:
        mqtt.publish(topic, data)


def get_total_readings(nodeIDs: list[str]) -> list[TotalReading]:
    readings = []

    for nodeID in nodeIDs:
        node_readings: list[TotalReading] = TotalReading.objects(nodeID=nodeID)

        for node_reading in node_readings:
            readings.append(node_reading.to_dashboard())

    return readings


def get_window_readings(nodeIDs: list[str]) -> list[WindowReading]:
    readings = []

    for nodeID in nodeIDs:
        node_readings: list[WindowReading] = WindowReading.objects(nodeID=nodeID)

        for node_reading in node_readings:
            readings.append(node_reading.to_dashboard())

    return readings
