import os
from datetime import datetime

import iso8601

from .. import mqtt
from ..services.database import Alert, Application, Data, Node, Reading
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


def publish(applicationID: str, sensorID: int, record: dict) -> dict:
    record["data"] = decode_data(record["data"])

    # Vero se arriva da chirpstack
    if "txInfo" in record:
        # TODO: portare a payload di node/app.py
        pass

    application = Application.objects(id=applicationID).first()

    if application is None:
        raise ObjectNotFoundException(Application)

    node = Node.objects(sensorID=sensorID).first()

    if node is None:
        node = Node(
            nodeID=record["nodeID"],
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

        requestedAt = iso8601.parse_date(record["requestedAt"])
        reading = Reading.objects(requestedAt=requestedAt).first()

        data = Data(
            payloadType=record["data"]["payloadType"],
            sensorData=record["data"]["sensorData"],
            publishedAt=iso8601.parse_date(record["publishedAt"]),
            mobius_sensorId=record["data"]["mobius_sensorId"],
            mobius_sensorPath=record["data"]["mobius_sensorPath"],
        )

        if reading is None:
            reading = Reading(
                node=node,
                requestedAt=requestedAt,
                data=[data],
            )
        else:
            reading["data"].append(data)

        reading.save()

        if data["sensorData"] >= MAX_TRESHOLD:
            alert = Alert(reading=reading, node=node, isHandled=False)
            alert.save()

    node["lastSeenAt"] = datetime.now()
    node["state"] = update_state(
        node["state"],
        node["lastSeenAt"],
        record["data"]["payloadType"],
        record["data"]["sensorData"],
    )
    node.save()

    return record


def send_mqtt_command(applicationID: str, nodeID: str, command: int):
    topic: str = f"{applicationID}/{nodeID}/command"

    data: bytes = encode_mqtt_data(command, datetime.now().isoformat())

    if not DISABLE_MQTT:
        mqtt.publish(topic, data)
