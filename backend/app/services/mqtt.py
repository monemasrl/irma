import json
import logging
import re
from datetime import datetime

from beanie import PydanticObjectId
from beanie.operators import And, Eq
from fastapi_mqtt import FastMQTT, MQTTConfig

from ..config import MQTTConfig as MQTTConfigInternal
from ..models.payload import ReadingPayload
from ..utils.enums import EventType, NodeState
from ..utils.node import on_launch, update_state
from ..utils.payload import handle_payload
from .database.models import Application, Node

logger = logging.getLogger(__name__)

STATUS_TOPIC = "+/+/status"
PAYLOAD_TOPIC = "+/+/payload"


def init_mqtt(conf: MQTTConfigInternal) -> FastMQTT:
    mqtt_config = MQTTConfig(
        host=conf.host,
        port=conf.port,
        ssl=conf.tls_enabled,
        username=conf.username,
        password=conf.password,
    )

    mqtt = FastMQTT(config=mqtt_config)

    @mqtt.on_connect()
    def connect(client, flags, rc, properties):
        logger.info("Connected to MQTT broker")

        for topic in [STATUS_TOPIC, PAYLOAD_TOPIC]:
            mqtt.client.subscribe(topic)
            logger.info(f"Subscribed to '{topic}'")

    @mqtt.on_message()
    async def on_message(client, topic: str, payload: bytes, qos, properties):
        from .. import socketManager

        logger.debug(f"Someone published '{payload.decode()}' on '{topic}'")

        topic_sliced = topic.split("/")

        try:
            applicationID = topic_sliced[0]
            nodeID = topic_sliced[1]
            topic = topic_sliced[2]
            value = payload.decode()

            if not nodeID.isnumeric():
                logger.error("nodeID '%s' is not parsable", nodeID)
                return

            application = await Application.get(PydanticObjectId(applicationID))
            if application is None:
                logger.error(f"Couldn't find applicationID '{applicationID}'")
                return

            node = await Node.find_one(
                And(
                    Eq(Node.nodeID, int(nodeID)),
                    Eq(Node.application, PydanticObjectId(applicationID)),
                )
            )

            if node is not None:
                node.lastSeenAt = datetime.now()

            if topic == "status" and re.match("^launch:.+", value):
                if node is None:
                    node = Node(
                        nodeID=int(nodeID),
                        application=application.id,
                        nodeName=value.split(":")[1],
                        state=NodeState.READY,
                        lastSeenAt=datetime.now(),
                    )

                new_state = update_state(
                    node.state, node.lastSeenAt, EventType.ON_LAUNCH
                )
                await node.save()

                await on_launch(node)
                socketManager.emit("change")
                return

            if node is None:
                logger.info(
                    "Detected unregistered Node '{%s}', applicationID '{%s}'. \
                     Restart it to get it registered",
                    nodeID,
                    applicationID,
                )
                return

            changed: bool = False

            if topic == "status":
                if value == "start":
                    new_state = update_state(
                        node.state, node.lastSeenAt, EventType.START_REC
                    )
                    changed = node.state != new_state
                    node.state = new_state
                    await node.save()

                elif value == "stop":
                    new_state = update_state(
                        node.state, node.lastSeenAt, EventType.STOP_REC
                    )
                    changed = node.state != new_state
                    node.state = new_state
                    await node.save()

                elif value == "keepalive":
                    new_state = update_state(
                        node.state, node.lastSeenAt, EventType.KEEP_ALIVE
                    )
                    changed = node.state != new_state
                    node.state = new_state
                    await node.save()

                else:
                    logger.error(
                        "Invalid value '{%s}' for sub-topic '{%s}'", value, topic
                    )
            elif topic == "payload":
                data_dict = json.loads(value)
                reading_payload: ReadingPayload = ReadingPayload.parse_obj(data_dict)

                await handle_payload(reading_payload)

            else:
                logger.error("Invalid sub-topic '{%s}'", topic)

            if changed:
                socketManager.emit("change")

        except IndexError as error:
            logger.error("Invalid topic '{%s}': {%s}", topic, error)

    return mqtt
