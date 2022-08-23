import base64
from datetime import datetime
from enum import IntEnum, auto
from os import environ
from time import sleep
from typing import Union

import paho.mqtt.client as mqtt
import requests
import yaml
from can import Message
from can.interface import Bus

BYPASS_CAN = bool(environ.get("BYPASS_CAN", 0))


class PayloadType(IntEnum):
    READING = 0
    START_REC = auto()
    END_REC = auto()
    KEEP_ALIVE = auto()
    HANDLE_ALERT = auto()


class CommandType(IntEnum):
    START_REC = 0


"""
encoded data
| 1 byte payload_type | 4 byte data | 10 byte sensorId | 10 byte sensorPath |
"""


def encode_data(
    payload_type: int, data: int, mobius_sensorId: str, mobius_sensorPath: str
) -> str:

    bytes = b""
    bytes += payload_type.to_bytes(1, "big")
    bytes += data.to_bytes(4, "big")
    bytes += mobius_sensorId.ljust(10).encode()
    bytes += mobius_sensorPath.ljust(10).encode()

    return base64.b64encode(bytes).decode()


def decode_mqtt_data(encoded_string: str) -> dict:
    encoded_data = base64.b64decode(encoded_string)
    return {
        "command": int.from_bytes(encoded_data[:1], "big"),
        "commandTimestamp": encoded_data[1:].decode(),
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

            self.bus = Bus(bustype=bustype, channel=channel, bitrate=bitrate) # type: ignore
            print(f"Can type '{bustype}', on channel '{channel}' @{bitrate}")

        self.send_keep_alive()
        self.init_mqtt_client()

    def init_mqtt_client(self):
        self.client = mqtt.Client()

        def on_connect(client, userdata, flags, rc):
            print("Connected with result code "+str(rc))

            applicationID = self.config["node_info"]["applicationID"]
            sensorID = self.config["node_info"]["sensorID"]
            client.subscribe(f"{applicationID}/{sensorID}/command")

        def on_message(client, userdata, msg: mqtt.MQTTMessage):
            print(msg.topic+" -> "+str(msg.payload))

            decoded_data = decode_mqtt_data(msg.payload.decode())

            command = decoded_data["command"]

            if command == CommandType.START_REC:
                self.start_rec(decoded_data["commandTimestamp"])

        self.client.on_connect = on_connect
        self.client.on_message = on_message

        self.client.connect(self.config['mqtt']['url'], self.config['mqtt']['port'], 60)

    def loop_forever(self):
        return self.client.loop_forever()

    def send_data(self, data: int, payload_type: PayloadType,
                  commandTimestamp: str = ""):
        payload: dict = {
            "sensorID": self.config["node_info"]["sensorID"],
            "sensorName": self.config["node_info"]["sensorName"],
            "applicationID": self.config["node_info"]["applicationID"],
            "organizationID": self.config["node_info"]["organizationID"],
            "data": encode_data(payload_type.value,
                                data,
                                self.config["mobius"]["sensorId"],
                                self.config["mobius"]["sensorPath"]),
            "publishedAt": datetime.now().isoformat(),
            "requestedAt": commandTimestamp,
        }

        host = self.config["microservice"]["url"]
        port = self.config["microservice"]["port"]
        api_key = self.config["microservice"]["api_key"]
        sensorID = self.config["node_info"]["sensorID"]
        applicationID = self.config["node_info"]["applicationID"]

        requests.post(
            url=f'{host}:{port}/api/{applicationID}/{sensorID}/publish',
            json=payload,
            headers={
                "Authorization": f'Bearer {api_key}',
                "Content-Type": "application/json"
            }
        )

    def send_keep_alive(self):
        self.send_data(0, PayloadType.KEEP_ALIVE)

    def read_and_send(self, commandTimestamp: str = ""):
        if BYPASS_CAN:
            data = int(input("Inserisci un dato: "))
            self.send_data(data, PayloadType.READING, commandTimestamp)
            return

        self.bus

        msg: Union[None, Message] = None

        while msg is None:
            msg = self.bus.recv(timeout=0.5)

        data: int = int.from_bytes(msg.data, byteorder='big', signed=False)
        print(f"CAN> {data}")

        self.send_data(data, PayloadType.READING, commandTimestamp)

    def start_rec(self, commandTimestamp: str):
        print("Received MQTT message, sending rec start...")

        self.send_data(0, PayloadType.START_REC)

        print("Sleeping for 10 seconds...")

        for _ in range(10):
            sleep(1)
            print(".", end="")

        print()

        print("Sending readings...")

        self.read_and_send(commandTimestamp)
        self.read_and_send(commandTimestamp)
        self.read_and_send(commandTimestamp)
        self.read_and_send(commandTimestamp)

        print("Sending rec end...")

        self.send_data(0, PayloadType.END_REC)


if __name__ == "__main__":
    node = Node()

    node.loop_forever()

