import json
import logging
import re
from datetime import datetime

from beanie import PydanticObjectId
from fastapi_mqtt import FastMQTT, MQTTConfig

from ..config import MQTTConfig as MQTTConfigInternal
from ..entities.node import Node
from ..models.payload import ReadingPayload
from ..utils.enums import NodeState
from ..utils.payload import handle_payload

logger = logging.getLogger(__name__)

STATUS_TOPIC = "+/+/status"
PAYLOAD_TOPIC = "+/+/payload"


def publish(topic: str, data: bytes | str):
    if isinstance(data, str):
        data = data.encode()

    from .. import mqtt

    logger.info("Publishing '%s' to '%s'", data, topic)

    if mqtt:
        mqtt.publish(topic, data)


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

            nodeID = int(nodeID)

            node: Node | None = await Node.from_id(nodeID, applicationID)

            if topic == "status" and re.match("^launch:.+", value):
                if node is None:
                    node = Node(
                        nodeID=int(nodeID),
                        application=PydanticObjectId(applicationID),
                        nodeName=value.split(":")[1],
                        state=NodeState.READY,
                        lastSeenAt=datetime.now(),
                    )

                await node.just_seen()
                await node.on_launch()

                socketManager.emit("change-node")
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
            await node.just_seen()

            if topic == "status":
                if value == "start":
                    await node.on_start_rec()
                    changed = True

                elif value == "stop":
                    await node.on_stop_rec()
                    changed = True

                elif value == "keepalive":
                    pass

                else:
                    logger.error(
                        "Invalid value '{%s}' for sub-topic '{%s}'", value, topic
                    )
            elif topic == "payload":
                data_dict = json.loads(value)
                reading_payload: ReadingPayload = ReadingPayload.parse_obj(data_dict)

                await handle_payload(node, reading_payload)
                socketManager.emit("change-reading")

            else:
                logger.error("Invalid sub-topic '{%s}'", topic)

            if changed:
                socketManager.emit("change-node")

        except IndexError as error:
            logger.error("Invalid topic '{%s}': {%s}", topic, error)

    return mqtt
