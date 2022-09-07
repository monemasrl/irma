import os
from datetime import datetime

from .. import mqtt
from ..services.database import Alert, Application, Node, Reading
from ..services.mobius.utils import insert
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

    if record["data"]["payloadType"] == PayloadType.READING:

        if MOBIUS_URL != "":
            insert(record)

        reading = Reading(
            nodeID=nodeID,
            canID=record["data"]["canID"],
            sensorNumber=record["data"]["sensorNumber"],
            sessionID=record["data"]["sessionID"],
            dangerLevel=record["data"]["dangerLevel"],
            window1_count=record["data"]["window1_count"],
            window2_count=record["data"]["window2_count"],
            window3_count=record["data"]["window3_count"],
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

    node["lastSeenAt"] = datetime.now()
    node["state"] = update_state(
        node["state"],
        node["lastSeenAt"],
        record["data"]["payloadType"],
        record["data"]["dangerLevel"],
    )
    node.save()

    return record


def send_mqtt_command(applicationID: str, nodeID: str, command: int):
    topic: str = f"{applicationID}/{nodeID}/command"

    data: bytes = encode_mqtt_data(command, datetime.now().isoformat())

    if not DISABLE_MQTT:
        mqtt.publish(topic, data)


def get_readings(nodeIDs: list[str]) -> list[dict]:
    readings = []

    for nodeID in nodeIDs:
        node_readings: list[Reading] = Reading.objects(nodeID=nodeID)

        for node_reading in node_readings:
            readings.append(node_reading.to_dashboard())

    return readings
