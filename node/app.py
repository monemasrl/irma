import base64
import threading
from enum import IntEnum, auto
from os import environ
from time import sleep
from typing import Union

import paho.mqtt.client as mqtt
import requests
import yaml
from can import Message
from commands import DecodedMessage, IrmaBus, MessageType

BYPASS_CAN = bool(environ.get("BYPASS_CAN", 0))


class PayloadType(IntEnum):
    READING = 0
    START_REC = auto()
    END_REC = auto()
    KEEP_ALIVE = auto()
    HANDLE_ALERT = auto()


class CommandType(IntEnum):
    START_REC = 0


#                           ENCODED DATA
# | 1 byte payload_type | 1 byte dangerLevel | 1 byte w1_count |
# | 1 byte w2_count | 1 byte w3_count |


def encode_data(
    payload_type: int,
    canID: int,
    sensorNumber: int,
    dangerLevel: int,
    window1_count: int,
    window2_count: int,
    window3_count: int,
    session_id: int,
) -> str:

    byts = b""
    byts += payload_type.to_bytes(1, "big")
    byts += canID.to_bytes(1, "big")
    byts += sensorNumber.to_bytes(1, "big")
    byts += dangerLevel.to_bytes(1, "big")
    byts += window1_count.to_bytes(1, "big")
    byts += window2_count.to_bytes(1, "big")
    byts += window3_count.to_bytes(1, "big")
    byts += session_id.to_bytes(1, "big")

    return base64.b64encode(byts).decode()


def decode_mqtt_data(encoded_string: str) -> dict:
    encoded_data = base64.b64decode(encoded_string)
    return {
        "command": int.from_bytes(encoded_data[:1], "big"),
        "commandTimestamp": int.from_bytes(encode_data[1:], "big"),
    }


class Node:
    def __init__(self):
        with open("config.yaml", "r") as file:
            loaded_yaml = yaml.load(file, Loader=yaml.Loader)
            self.config = loaded_yaml["settings"]

        if not BYPASS_CAN:
            bustype = self.config["can"]["bustype"]
            channel = self.config["can"]["channel"]
            bitrate = self.config["can"]["bitrate"]

            self.bus = IrmaBus(bustype=bustype, channel=channel, bitrate=bitrate)
            print(f"Can type '{bustype}', on channel '{channel}' @{bitrate}")

        self.launch_keep_alive_daemon()
        self.init_mqtt_client()

    def init_mqtt_client(self):
        self.client = mqtt.Client()

        def on_connect(client, userdata, flags, rc):
            print("Connected with result code " + str(rc))

            applicationID = self.config["node_info"]["applicationID"]
            nodeID = self.config["node_info"]["nodeID"]
            client.subscribe(f"{applicationID}/{nodeID}/command")

        def on_message(client, userdata, msg: mqtt.MQTTMessage):
            print(msg.topic + " -> " + str(msg.payload))

            decoded_data = decode_mqtt_data(msg.payload.decode())

            command = decoded_data["command"]

            if command == CommandType.START_REC:
                self.start_rec(decoded_data["commandTimestamp"])

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
        if message["message_type"] == MessageType.GET_TOTAL_COUNT:
            # TODO: finish
            self.send_data(
                PayloadType.READING,
                int(message["n_detector"]),
                int(message["sipm"]),
                message["danger_level"],
            )

    def send_data(
        self,
        payload_type: PayloadType,
        canID: int = 0,
        sensorNumber: int = 0,
        dangerLevel: int = 0,
        window1_count: int = 0,
        window2_count: int = 0,
        window3_count: int = 0,
        sessionID: int = 0,
    ):
        payload: dict = {
            "nodeID": self.config["node_info"]["nodeID"],
            "nodeName": self.config["node_info"]["nodeName"],
            "applicationID": self.config["node_info"]["applicationID"],
            "organizationID": self.config["node_info"]["organizationID"],
            "data": encode_data(
                payload_type.value,
                canID,
                sensorNumber,
                dangerLevel,
                window1_count,
                window2_count,
                window3_count,
                sessionID,
            ),
        }

        host = self.config["microservice"]["url"]
        port = self.config["microservice"]["port"]
        api_key = self.config["microservice"]["api_key"]

        requests.post(
            url=f"{host}:{port}/api/payload/publish",
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
        while True:
            self.send_data(PayloadType.KEEP_ALIVE)
            sleep(seconds)

    def read_and_send(self, sessionID: int = 0):
        if BYPASS_CAN:
            canID = int(input("Inserisci canID: "))
            sensorNumber = int(input("Inserisci sensorNumber: "))
            dangerLevel = int(input("Inserisci dangerLevel: "))
            w1_count = int(input("Inserisci w1_count: "))
            w2_count = int(input("Inserisci w2_count: "))
            w3_count = int(input("Inserisci w3_count: "))
            self.send_data(
                PayloadType.READING,
                canID,
                sensorNumber,
                dangerLevel,
                w1_count,
                w2_count,
                w3_count,
                sessionID,
            )
            return

        msg: Union[None, Message] = None

        while msg is None:
            msg = self.bus.recv(timeout=0.5)

        data: int = int.from_bytes(msg.data, byteorder="big", signed=False)
        print(f"CAN> {data}")

        # TODO:
        self.send_data(PayloadType.READING, sessionID=sessionID)

    def start_rec(self, sessionID: int):
        print("Received MQTT message, sending rec start...")

        self.send_data(PayloadType.START_REC)

        print("Sending readings...")

        self.read_and_send(sessionID)
        self.read_and_send(sessionID)
        self.read_and_send(sessionID)
        self.read_and_send(sessionID)

        print("Sending rec end...")

        self.send_data(PayloadType.END_REC)


if __name__ == "__main__":
    node = Node()

    node.loop_forever()
