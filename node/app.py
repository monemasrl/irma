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
            client.subscribe(f"{applicationID}/{nodeID}/#")

        def on_message(client, userdata, msg: mqtt.MQTTMessage):
            print(f"Someone published '{str(msg.payload)}' on '{msg.topic}'")

            topic_sliced = msg.topic.split("/")[2:]
            value = msg.payload.decode()

            try:
                if topic_sliced[0] == "rec":
                    self.handle_rec_message(value)
                elif topic_sliced[0] == "demo":
                    self.handle_demo_message(value)
                elif (
                    len(topic_sliced) > 2
                    and topic_sliced[0] in ["1", "2", "3", "4"]
                    and topic_sliced[1] in ["1", "2"]
                    and value.isnumeric()
                ):
                    self.handle_sipm_message(
                        int(topic_sliced[0]),
                        int(topic_sliced[1]),
                        topic_sliced[2:],
                        int(value),
                    )

                print(f"Invalid command on topic '{msg.topic}', value '{value}'")

            except ValueError as error:
                print(f"Caught exception on topic '{msg.topic}': {error}")

        self.client.on_connect = on_connect
        self.client.on_message = on_message

        self.client.connect(self.config["mqtt"]["url"], self.config["mqtt"]["port"], 60)

    def handle_rec_message(self, value: str):
        if value == "start":
            return self.start_rec(0)
        elif value == "stop":
            return self.stop_rec()
        raise ValueError(f"Invalid value '{value}'")

    def handle_demo_message(self, value: str):
        if value == "1":
            return self.start_rec(1)
        elif value == "2":
            return self.start_rec(2)
        raise ValueError(f"Invalid value '{value}'")

    def handle_sipm_message(
        self, detector: int, sipm: int, sub_command: list[str], value: int
    ):
        if sub_command[0] == "hv":
            return self.bus.set_hv(
                detector,
                sipm,
                value,
            )

        elif sub_command[0] in ["1", "2", "3"] and len(sub_command) > 1:
            if sub_command[1] == "low":
                return self.bus.set_window_low(
                    detector,
                    sipm,
                    int(sub_command[0]),
                    value,
                )

            elif sub_command[1] == "high":
                return self.bus.set_window_high(
                    detector,
                    sipm,
                    int(sub_command[0]),
                    value,
                )

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
        self.send_http_payload(PayloadType.END_REC)
        while True:
            sleep(seconds)
            self.send_http_payload(PayloadType.KEEP_ALIVE)

    def start_rec(self, mode: int):
        print("Received MQTT message, sending rec start...")

        self.send_http_payload(PayloadType.START_REC)
        self.bus.start_session(mode)

    def stop_rec(self):
        print("Received MQTT message, sending rec end...")

        self.send_http_payload(PayloadType.END_REC)
        self.bus.stop_session()


if __name__ == "__main__":
    node = Node()

    node.loop_forever()
