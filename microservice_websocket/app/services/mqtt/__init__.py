from datetime import datetime

from beanie import PydanticObjectId
from beanie.operators import And, Eq
from paho.mqtt.client import Client as MQTTClient, MQTTMessage

from ...config import MQTTConfig
from ...utils.enums import EventType
from ...utils.node import update_state
from ..database.models import Node


def init_mqtt(mqtt_config: MQTTConfig) -> MQTTClient:
    mqtt = MQTTClient()
    if mqtt_config.tls_enabled:
        mqtt.tls_set()

    mqtt.username_pw_set(mqtt_config.username, mqtt_config.password)
    mqtt.connect(host=mqtt_config.host, port=mqtt_config.port)
    mqtt.subscribe("+/+/status")

    async def on_message(client, userdata, msg: MQTTMessage):
        from ... import socketManager

        print(f"Someone published '{str(msg.payload)}' on '{msg.topic}'")

        topic_sliced = msg.topic.split("/")

        try:
            applicationID = topic_sliced[0]
            nodeID = topic_sliced[1]
            topic = topic_sliced[2]
            value = msg.payload.decode()

            node = await Node.find_one(
                And(
                    Eq(Node.nodeID, nodeID),
                    Eq(Node.application, PydanticObjectId(applicationID)),
                )
            )
            if node is None:
                print(f"Couldn't find node '{nodeID}', applicationID '{applicationID}'")
                return

            node.lastSeenAt = datetime.now()

            if topic == "status":
                if value == "start":
                    node.state = update_state(
                        node.state, node.lastSeenAt, EventType.START_REC
                    )
                    await node.save()
                    await socketManager.emit("change")
                elif value == "stop":
                    node.state = update_state(
                        node.state, node.lastSeenAt, EventType.STOP_REC
                    )
                    await node.save()
                    await socketManager.emit("change")
                else:
                    print(f"Invalid value '{value}' for sub-topic '{topic}'")
            else:
                print(f"Invalid sub-topic '{topic}'")
        except IndexError as error:
            print(f"Invalid topic '{msg.topic}': {error}")

    mqtt.on_message = on_message

    mqtt.loop_start()

    return mqtt
