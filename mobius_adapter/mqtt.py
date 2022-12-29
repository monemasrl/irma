import json

from paho.mqtt.client import Client, MQTTMessage

from utils import send


def register_callbacks(client: Client):
    def on_connect(client: Client, userdata, flags, rc):
        print("[INFO] Connected to MQTT broker")

        client.subscribe("+/+/payload")
        client.subscribe("+/+/status")

        print("[INFO] Subscribed to '+/+/payload' and '+/+/status'")

    def on_message(client, userdata, msg: MQTTMessage):
        print(f"[INFO] Received '{msg.payload.decode()}' from '{msg.topic}'")

        applicationID, nodeID, topic = msg.topic.split("/")
        nodeID = int(nodeID)

        payload = msg.payload.decode()

        if topic == "status":
            sensor_data = {"payloadType": "status", "value": payload}

        elif topic == "payload":
            decoded_data = json.loads(payload)

            if decoded_data["payloadType"] == "window":
                decoded_data["payloadType"] = f"w{decoded_data['data']['value']}"
                decoded_data["data"]["value"] = decoded_data["data"]["count"]

            sensor_data = {
                "payloadType": decoded_data["payloadType"],
                "value": decoded_data["data"]["value"],
                "canID": decoded_data["data"]["canID"],
                "sensorNumber": decoded_data["data"]["sensorNumber"],
                "sessionID": decoded_data["data"]["sessionID"],
                "readingID": decoded_data["data"]["readingID"],
            }
        else:
            raise ValueError(f"Invalid topic '{topic}'")

        send(nodeID, sensor_data)

    client.on_connect = on_connect
    client.on_message = on_message
