import base64
from datetime import datetime
from time import sleep
from typing import Union
from can import Message
from enum import IntEnum, auto
import requests
import paho.mqtt.client as mqtt
import yaml
from can.interface import Bus

config: dict = {}

with open("config.yaml", "r") as file:
    loaded_yaml = yaml.load(file, Loader=yaml.Loader) 
    config = loaded_yaml["settings"]


class RecordingState(IntEnum):
    NOT_RECORDING = 0
    BEGIN_REC = auto()
    END_REC = auto()


class Command(IntEnum):
    START_RECORDING = 0


"""
encoded data
| 1 byte state | 4 byte data | 10 byte sensorId | 10 byte sensorPath |
"""

def encode_data(state: int, data: int,
                mobius_sensorId: str,
                mobius_sensorPath: str) -> str:

    bytes = b''
    bytes += state.to_bytes(1, 'big')
    bytes += data.to_bytes(4, 'big')
    bytes += mobius_sensorId.ljust(10).encode()
    bytes += mobius_sensorPath.ljust(10).encode()

    return base64.b64encode(bytes).decode()


def send_data(data: int, recording_state: RecordingState):
    payload: dict = {
        "sensorID": config["node_info"]["sensorID"],
        "sensorName": config["node_info"]["sensorName"],
        "applicationID": config["node_info"]["applicationID"],
        "organizationID": config["node_info"]["organizationID"],
        "data": encode_data(recording_state.value,
                            data,
                            config["mobius"]["sensorId"],
                            config["mobius"]["sensorPath"]),
        "publishedAt": datetime.now().isoformat()
    }

    host = config["microservice"]["url"]
    port = config["microservice"]["port"]
    api_key = config["microservice"]["api_key"]
    sensorID = config["node_info"]["sensorID"]
    applicationID = config["node_info"]["applicationID"]

    requests.post(
        url=f'{host}:{port}/api/{applicationID}/{sensorID}/publish',
        data=payload,
        headers={
            "Authorization": f'Bearer {api_key}'
        }
    )


def init_can(bustype, channel, bitrate):
    global bus
    bus = Bus(bustype=bustype, channel=channel, bitrate=bitrate) # type: ignore

    print(f"Can type '{bustype}', on channel '{channel}' @{bitrate}")


def read_and_send():
    global bus

    msg: Union[None, Message] = None
    
    while msg is None:
        msg = bus.recv(timeout=0.5)

    data: int = int.from_bytes(msg.data, byteorder='big', signed=False)
    print(f"CAN> {data}")

    send_data(data, RecordingState.NOT_RECORDING)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # TODO: riguardare
    applicationID = config["node_info"]["applicationID"]
    sensorID = config["node_info"]["sensorID"]
    client.subscribe(f"{applicationID}/{sensorID}/commands")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg: mqtt.MQTTMessage):
    print(msg.topic+" -> "+str(msg.payload))

    decoded_num = int.from_bytes(msg.payload, 'big')

    if decoded_num == Command.START_RECORDING:

        print("Received MQTT message, sending rec start...")

        send_data(0, RecordingState.BEGIN_REC)

        print("Sleeping for 10 seconds...")

        for _ in range(10):
            sleep(1)
            print(".", end="")

        print()

        print("Sending readings...")

        read_and_send()

        print("Sending rec end...")

        send_data(0, RecordingState.END_REC)


if __name__ == "__main__":

    init_can('socketcan', 'can0', 12500)

    read_and_send()

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(config['mqtt']['url'], config['mqtt']['port'], 60)

    client.loop_forever()

