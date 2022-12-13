#
# def create_mqtt(app: Flask) -> Mqtt:
#     mqtt = Mqtt(app)
#
#     @mqtt.on_connect()
#     def handle_connect(client, userdata, flags, rc):
#         mqtt.subscribe("application")
#
#     @mqtt.on_message()
#     def handle_mqtt_message(client, userdata, message):
#         pass
#
#     return mqtt

from paho.mqtt.client import Client as MQTTClient
from paho.mqtt.client import MQTTMessage

from ...config import MQTTConfig


def init_mqtt(mqtt_config: MQTTConfig) -> MQTTClient:
    mqtt = MQTTClient()
    if mqtt_config.tls_enabled:
        mqtt.tls_set()

    mqtt.username_pw_set(mqtt_config.username, mqtt_config.password)
    mqtt.connect(host=mqtt_config.host, port=mqtt_config.port)
    mqtt.subscribe("+/+/status")

    def on_message(client, userdata, msg: MQTTMessage):
        print(f"Someone published '{str(msg.payload)}' on '{msg.topic}'")

        topic_sliced = msg.topic.split("/")

        try:
            applicationID = topic_sliced[0]
            nodeID = topic_sliced[1]
            topic = topic_sliced[2]
            value = msg.payload.decode()

            if topic == "status":
                if value == "start":
                    pass
                else:
                    print(f"Invalid value '{value}' for sub-topic '{topic}'")
            else:
                print(f"Invalid sub-topic '{topic}'")
        except IndexError as error:
            print(f"Invalid topic '{msg.topic}'")

    mqtt.on_message = on_message

    mqtt.loop_start()

    return mqtt
