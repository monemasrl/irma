import base64
import threading
from datetime import datetime, timedelta
from time import sleep
from typing import Union
from can import Message
from enum import IntEnum, auto
import requests
import paho.mqtt.client as mqtt
import yaml
from os import environ
from can.interface import Bus

BYPASS_CAN = bool(environ.get("BYPASS_CAN", 0))

config: dict = {}

with open("config.yaml", "r") as file:
    loaded_yaml = yaml.load(file, Loader=yaml.Loader) 
    config = loaded_yaml["settings"]


class PayloadType(IntEnum):
    READING=0
    START_REC=auto()
    END_REC=auto()
    KEEP_ALIVE=auto()
    HANDLE_ALERT=auto()


class CommandType(IntEnum):
    START_REC=0


"""
encoded data
| 1 byte payload_type | 4 byte data | 10 byte sensorId | 10 byte sensorPath |
"""

def encode_data(payload_type: int, data: int,
                mobius_sensorId: str,
                mobius_sensorPath: str) -> str:

    bytes = b''
    bytes += payload_type.to_bytes(1, 'big')
    bytes += data.to_bytes(4, 'big')
    bytes += mobius_sensorId.ljust(10).encode()
    bytes += mobius_sensorPath.ljust(10).encode()

    return base64.b64encode(bytes).decode()


def decode_mqtt_data(encoded_string: str) -> dict:
    encoded_data = base64.b64decode(encoded_string)
    return {
        "command": int.from_bytes(encoded_data[:1], 'big'),
        "commandTimestamp": encoded_data[1:].decode()
    }


def send_data(data: int, payload_type: PayloadType,
              commandTimestamp: str = ""):
    payload: dict = {
        "sensorID": config["node_info"]["sensorID"],
        "sensorName": config["node_info"]["sensorName"],
        "applicationID": config["node_info"]["applicationID"],
        "organizationID": config["node_info"]["organizationID"],
        "data": encode_data(payload_type.value,
                            data,
                            config["mobius"]["sensorId"],
                            config["mobius"]["sensorPath"]),
        "publishedAt": datetime.now().isoformat(),
        "requestedAt": commandTimestamp,
    }

    host = config["microservice"]["url"]
    port = config["microservice"]["port"]
    api_key = config["microservice"]["api_key"]
    sensorID = config["node_info"]["sensorID"]
    applicationID = config["node_info"]["applicationID"]

    requests.post(
        url=f'{host}:{port}/api/{applicationID}/{sensorID}/publish',
        json=payload,
        headers={
            "Authorization": f'Bearer {api_key}',
            "Content-Type": "application/json"
        }
    )

def launch_keep_alive_daemon():
    thread = threading.Thread(target=periodically_send_keep_alive, daemon=True)
    thread.start()

def periodically_send_keep_alive():
    seconds = config["microservice"]["keep_alive_seconds"]
    while True:
        sleep(seconds)
        send_keep_alive()


def send_keep_alive():
    send_data(0, PayloadType.KEEP_ALIVE)


def init_can(bustype, channel, bitrate):
    global bus
    bus = Bus(bustype=bustype, channel=channel, bitrate=bitrate) # type: ignore

    print(f"Can type '{bustype}', on channel '{channel}' @{bitrate}")


def read_and_send(commandTimestamp: str = ""):
    if BYPASS_CAN:
        data = int(input("Inserisci un dato: "))
        send_data(data, PayloadType.READING, commandTimestamp)
        return

    global bus

    msg: Union[None, Message] = None
    
    while msg is None:
        msg = bus.recv(timeout=0.5)

    data: int = int.from_bytes(msg.data, byteorder='big', signed=False)
    print(f"CAN> {data}")

    send_data(data, PayloadType.READING, commandTimestamp)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # TODO: riguardare
    applicationID = config["node_info"]["applicationID"]
    sensorID = config["node_info"]["sensorID"]
    client.subscribe(f"{applicationID}/{sensorID}/command")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg: mqtt.MQTTMessage):
    print(msg.topic+" -> "+str(msg.payload))

    decoded_data = decode_mqtt_data(msg.payload.decode())

    command = decoded_data["command"]

    if command == CommandType.START_REC:

        print("Received MQTT message, sending rec start...")

        send_data(0, PayloadType.START_REC)

        print("Sleeping for 10 seconds...")

        for _ in range(10):
            sleep(1)
            print(".", end="")

        print()

        print("Sending readings...")

        read_and_send(decoded_data["commandTimestamp"])
        read_and_send(decoded_data["commandTimestamp"])
        read_and_send(decoded_data["commandTimestamp"])
        read_and_send(decoded_data["commandTimestamp"])

        print("Sending rec end...")

        send_data(0, PayloadType.END_REC)


if __name__ == "__main__":

    if not BYPASS_CAN:
        init_can('socketcan', 'can0', 12500)

    send_keep_alive()
    launch_keep_alive_daemon()

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(config['mqtt']['url'], config['mqtt']['port'], 60)

    client.loop_forever()

