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


class RecorginState(IntEnum):
    NOT_RECORDING = 0
    BEGIN_REC = auto()
    END_REC = auto()


def send_data(data: int, recording_state: RecorginState):
    payload: dict = {
        "applicationID": config["node_info"]["applicationID"],
        "organizationID": config["node_info"]["organizationID"],
        "data": {
            "state": recording_state.value,
            "sensorData": data,
            "sensorId": config["node_info"]["sensorId"],
            "sensorPath": config["node_info"]["sensorPath"],
        },
        "publishedAt": datetime.now().isoformat()
    }
    
    host = config["microservice"]["url"]
    port = config["microservice"]["port"]
    api_key = config["microservice"]["api_key"]
    route = config["node_info"]["sensorPath"]

    requests.post(
        url=f'{host}:{port}/{route}',
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

    send_data(data, RecorginState.NOT_RECORDING)


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # TODO: riguardare
    client.subscribe(f"{config['node_info']['sensorPath']}/rec")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" -> "+str(msg.payload))

    print("Received MQTT message, sending rec start...")

    send_data(0, RecorginState.BEGIN_REC)

    print("Sleeping for 10 seconds...")

    for _ in range(10):
        sleep(1)        
        print(".", end="")

    print()

    print("Sending readings...")

    read_and_send()

    print("Sending rec end...")

    send_data(0, RecorginState.END_REC)


if __name__ == "__main__":

    init_can('socketcan', 'can0', 12500)

    read_and_send()

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(config['mqtt']['url'], config['mqtt']['port'], 60)

    client.loop_forever()

