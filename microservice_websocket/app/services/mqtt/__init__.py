import json
from datetime import datetime
import re

from beanie import PydanticObjectId
from beanie.operators import And, Eq
from fastapi_mqtt import FastMQTT, MQTTConfig

from app.utils.payload import handle_payload

from ...models.payload import ReadingPayload

from ...config import MQTTConfig as MQTTConfigInternal
from ...utils.enums import EventType, NodeState
from ...utils.node import on_launch, update_state
from ..database.models import Node, Application

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
        print("[MQTT] Connected")
        for topic in [STATUS_TOPIC, PAYLOAD_TOPIC]:
            mqtt.client.subscribe(topic)
            print(f"[MQTT] Subscribed to '{topic}'")

    @mqtt.on_message()
    async def on_message(client, topic: str, payload: bytes, qos, properties):
        from ... import socketManager

        print(f"[MQTT] Someone published '{str(payload)}' on '{topic}'")

        topic_sliced = topic.split("/")

        try:
            applicationID = topic_sliced[0]
            nodeID = topic_sliced[1]
            topic = topic_sliced[2]
            value = payload.decode()

            if not nodeID.isnumeric():
                print("[MQTT] nodeID is not parsable")
                return

            application = await Application.get(PydanticObjectId(applicationID))
            if application is None:
                print(f"Couldn't find applicationID '{applicationID}'")
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
                print(
                    f"Detected unregistered Node '{nodeID}', applicationID '{applicationID}'. Restart it to get it registered"
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
                    print(f"Invalid value '{value}' for sub-topic '{topic}'")
            elif topic == "payload":
                data_dict = json.loads(value)
                reading_payload: ReadingPayload = ReadingPayload.parse_obj(data_dict)

                await handle_payload(reading_payload)

            else:
                print(f"Invalid sub-topic '{topic}'")

            if changed:
                socketManager.emit("change")

        except IndexError as error:
            print(f"Invalid topic '{topic}': {error}")

    return mqtt
