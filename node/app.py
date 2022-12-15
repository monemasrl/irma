import json
import threading
from enum import IntEnum, auto
from os import environ
from time import sleep
from typing import Optional

import paho.mqtt.client as mqtt
import requests
import yaml
from can_protocol import DecodedMessage, MessageType
from irma_bus import IrmaBus
from mock_bus import MockBus

BYPASS_CAN = bool(environ.get("BYPASS_CAN", 0))


class PayloadType(IntEnum):
    TOTAL_READING = 0
    WINDOW_READING = 1
    KEEP_ALIVE = 4
    ON_LAUNCH = 6


class EventType(IntEnum):
    START_REC = 0
    STOP_REC = auto()
    RAISE_ALERT = auto()
    HANDLE_ALERT = auto()
    KEEP_ALIVE = auto()
    ON_LAUNCH = auto()


class Node:
    def __init__(self):
        with open("config.yaml", "r") as file:
            loaded_yaml = yaml.load(file, Loader=yaml.Loader)
            self.config = loaded_yaml["settings"]

        if not BYPASS_CAN:
            bustype = self.config["can"]["bustype"]
            channel = self.config["can"]["channel"]
            bitrate = self.config["can"]["bitrate"]

            filter_id = self.config["can"].get("filter_id", None)
            filter_mask = self.config["can"].get("filter_mask", None)

            self.bus = IrmaBus(
                bustype=bustype,
                channel=channel,
                bitrate=bitrate,
                filter_id=filter_id,
                filter_mask=filter_mask,
            )
            print(f"Can type '{bustype}', on channel '{channel}' @{bitrate}")
        else:
            self.bus = MockBus()
            print("Started MockBus")

        self.launch_keep_alive_daemon()
        self.init_mqtt_client()

    def init_mqtt_client(self):
        self.client = mqtt.Client()

        applicationID = self.config["node_info"]["applicationID"]
        nodeID = self.config["node_info"]["nodeID"]
        self.topic = f"{applicationID}/{nodeID}"

        if self.config["mqtt"]["tls"]:
            self.client.tls_set()

        self.client.username_pw_set(
            self.config["mqtt"]["user"], self.config["mqtt"]["password"]
        )

        def on_connect(client, userdata, flags, rc):
            print("Connected with result code " + str(rc))

            client.subscribe(self.topic + "/command")
            client.subscribe(self.topic + "/set")

        def on_message(client, userdata, msg: mqtt.MQTTMessage):
            print(f"Someone published '{str(msg.payload)}' on '{msg.topic}'")

            topic_sliced = msg.topic.split("/")[2:]
            value = msg.payload.decode()

            try:
                if topic_sliced[0] == "command":
                    self.handle_command(value)
                elif topic_sliced[0] == "set":
                    self.handle_set(value)
                else:
                    print(f"Invalid command on topic '{msg.topic}', value '{value}'")

            except ValueError as error:
                print(f"Caught exception on topic '{msg.topic}': {error}")

        self.client.on_connect = on_connect
        self.client.on_message = on_message

        self.client.connect(self.config["mqtt"]["url"], self.config["mqtt"]["port"], 60)

    def handle_command(self, value: str):
        if value == "stop":
            self.stop_rec()
            return

        command, n = value.split(":")
        if command == "start" and n in ["0", "1", "2"]:
            self.start_rec(int(n))
            return

        raise ValueError(f"Invalid value '{value}'")

    def handle_set(self, value: str):
        payload = json.loads(value)

        try:
            detector = payload["detector"]
            if not isinstance(detector, int):
                raise ValueError(f"Invalid type for value 'detector': {type(detector)}")

            sipm = payload["sipm"]
            if not isinstance(sipm, int):
                raise ValueError(f"Invalid type for value 'sipm': {type(sipm)}")

            value = payload["value"]
            if not isinstance(value, int):
                raise ValueError(f"Invalid type for value 'value': {type(value)}")

            if payload["type"] == "hv":
                self.bus.set_hv(detector, sipm, value)
                return

            n = payload["n"]
            if not isinstance(n, int):
                raise ValueError(f"Invalid type for value 'n': {type(n)}")

            if payload["type"] == "window_low":
                self.bus.set_window_low(detector, sipm, n, value)
                return

            if payload["type"] == "window_high":
                self.bus.set_window_high(detector, sipm, n, value)
                return

            raise ValueError(f"Invalid type '{payload['type']}'")
        except KeyError as error:
            print(f"Error processing set payload: {error}")

    def loop_forever(self):
        while True:
            self.client.loop(0.1)
            message = self.bus.listen()
            if message is not None:
                self.send_message(message)

    def send_message(self, message: DecodedMessage):
        if message["message_type"] == MessageType.RETURN_COUNT_TOTAL:
            self.send_http_payload(PayloadType.TOTAL_READING, message)
        elif message["message_type"] == MessageType.RETURN_COUNT_WINDOW:
            self.send_http_payload(PayloadType.WINDOW_READING, message)
        else:
            raise ValueError(f"""Unexpected MessageType '{message["message_type"]}'""")

    def send_http_payload(
        self,
        payload_type: PayloadType,
        data: Optional[DecodedMessage] = None,
    ):

        if data is None:
            data_entry = None
        else:
            data_entry = {
                "canID": data["n_detector"],
                "sensorNumber": data["sipm"],
                "value": data["value"],
                "count": data["count"],
                "sessionID": data["sessionID"],
                "readingID": data["readingID"],
            }

        payload: dict = {
            "nodeID": self.config["node_info"]["nodeID"],
            "nodeName": self.config["node_info"]["nodeName"],
            "applicationID": self.config["node_info"]["applicationID"],
            "organizationID": self.config["node_info"]["organizationID"],
            "payloadType": payload_type,
            "data": data_entry,
        }

        host = self.config["microservice"]["url"]
        port = self.config["microservice"]["port"]
        api_key = self.config["microservice"]["api_key"]

        requests.post(
            url=f"{host}:{port}/api/payload/",
            json=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )

    def launch_keep_alive_daemon(self):
        thread = threading.Thread(target=self.periodically_send_keep_alive, daemon=True)
        thread.start()

    def periodically_send_keep_alive(self):
        seconds = self.config["microservice"]["keep_alive_seconds"]
        self.send_http_payload(PayloadType.ON_LAUNCH)
        while True:
            sleep(seconds)
            self.send_http_payload(PayloadType.KEEP_ALIVE)

    def start_rec(self, mode: int):
        print("Received MQTT message, sending rec start...")

        self.client.publish(self.topic + "/status", "start")
        self.bus.start_session(mode)

    def stop_rec(self):
        print("Received MQTT message, sending rec end...")

        self.client.publish(self.topic + "/status", "stop")
        self.bus.stop_session()


if __name__ == "__main__":
    node = Node()

    node.loop_forever()
