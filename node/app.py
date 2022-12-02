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
    WINDOW_READING = auto()
    START_REC = auto()
    END_REC = auto()
    KEEP_ALIVE = auto()
    HANDLE_ALERT = auto()


class CommandType(IntEnum):
    START_REC = 0
    END_REC = auto()
    SET_DEMO_1 = auto()
    SET_DEMO_2 = auto()


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

        if self.config["mqtt"]["tls"]:
            self.client.tls_set()

        self.client.username_pw_set(
            self.config["mqtt"]["user"], self.config["mqtt"]["password"]
        )

        def on_connect(client, userdata, flags, rc):
            print("Connected with result code " + str(rc))

            applicationID = self.config["node_info"]["applicationID"]
            nodeID = self.config["node_info"]["nodeID"]
            client.subscribe(f"{applicationID}/{nodeID}/command")

        def on_message(client, userdata, msg: mqtt.MQTTMessage):
            print(msg.topic + " -> " + str(msg.payload))

            command = int.from_bytes(msg.payload, "big")

            if command == CommandType.START_REC:
                self.start_rec(0)
            elif command == CommandType.END_REC:
                self.end_rec()
            elif command == CommandType.SET_DEMO_1:
                self.start_rec(1)
            elif command == CommandType.SET_DEMO_2:
                self.start_rec(2)

        self.client.on_connect = on_connect
        self.client.on_message = on_message

        self.client.connect(self.config["mqtt"]["url"], self.config["mqtt"]["port"], 60)

    def loop_forever(self):
        while True:
            self.client.loop(0.1)
            message = self.bus.listen()
            if message is not None:
                self.send_message(message)

    def send_message(self, message: DecodedMessage):
        if message["message_type"] == MessageType.RETURN_COUNT_TOTAL:
            self.send_data(PayloadType.TOTAL_READING, message)
        elif message["message_type"] == MessageType.RETURN_COUNT_WINDOW:
            self.send_data(PayloadType.WINDOW_READING, message)
        else:
            raise ValueError(f"""Unexpected MessageType '{message["message_type"]}'""")

    def send_data(
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
        self.send_data(PayloadType.END_REC)
        while True:
            sleep(seconds)
            self.send_data(PayloadType.KEEP_ALIVE)

    def start_rec(self, mode: int):
        print("Received MQTT message, sending rec start...")

        self.send_data(PayloadType.START_REC)
        self.bus.start_session(mode)

    def end_rec(self):
        print("Received MQTT message, sending rec end...")

        self.send_data(PayloadType.END_REC)
        self.bus.stop_session()


if __name__ == "__main__":
    node = Node()

    node.loop_forever()
