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


def init_mqtt(host: str, port: int, tls: bool = False) -> MQTTClient:
    mqtt = MQTTClient()
    if tls:
        mqtt.tls_set()

    mqtt.connect(host=host, port=port)
    mqtt.loop_start()

    return mqtt
