# from flask import Flask
# from flask_mqtt import Mqtt
#
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

from ...config import MQTTConfig


def init_mqtt(mqtt_config: MQTTConfig) -> MQTTClient:
    mqtt = MQTTClient()
    if mqtt_config.tls_enabled:
        mqtt.tls_set()

    mqtt.username_pw_set(mqtt_config.username, mqtt_config.password)

    mqtt.connect(host=mqtt_config.host, port=mqtt_config.port)
    mqtt.loop_start()

    return mqtt
