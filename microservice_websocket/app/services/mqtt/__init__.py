from datetime import datetime

from beanie import PydanticObjectId
from beanie.operators import And, Eq
from fastapi_mqtt import FastMQTT, MQTTConfig

from ...config import MQTTConfig as MQTTConfigInternal
from ...utils.enums import EventType
from ...utils.node import on_launch, update_state
from ..database.models import Node

STATUS_TOPIC = "+/+/status"


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
        mqtt.client.subscribe(STATUS_TOPIC)
        print(f"[MQTT] Subscribed to '{STATUS_TOPIC}'")

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

            node = await Node.find_one(
                And(
                    Eq(Node.nodeID, int(nodeID)),
                    Eq(Node.application, PydanticObjectId(applicationID)),
                )
            )
            if node is None:
                print(f"Couldn't find node '{nodeID}', applicationID '{applicationID}'")
                return

            node.lastSeenAt = datetime.now()

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

                elif value == "launch":
                    new_state = update_state(
                        node.state, node.lastSeenAt, EventType.ON_LAUNCH
                    )
                    changed = node.state != new_state
                    node.state = new_state
                    await node.save()
                    await on_launch(node)

                else:
                    print(f"Invalid value '{value}' for sub-topic '{topic}'")
            else:
                print(f"Invalid sub-topic '{topic}'")

            if changed:
                await socketManager.emit("change")

        except IndexError as error:
            print(f"Invalid topic '{topic}': {error}")

    return mqtt
