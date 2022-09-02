from flask import Flask
from flask_mqtt import Mqtt


def create_mqtt(app: Flask) -> Mqtt:
    mqtt = Mqtt(app)

    @mqtt.on_connect()
    def handle_connect(client, userdata, flags, rc):
        mqtt.subscribe("application")

    @mqtt.on_message()
    def handle_mqtt_message(client, userdata, message):
        pass

    return mqtt
