import json

from paho.mqtt.client import Client, MQTTMessage

from utils import Data, create_session_container, insert


def register_callbacks(client: Client):
    def on_connect(client: Client, userdata, flags, rc):
        print("[INFO] Connected to MQTT broker")

        client.subscribe("+/+/payload")
        client.subscribe("+/+/sessions")

        print("[INFO] Subscribed to '+/+/payload' and '+/+/status'")

    def on_message(client, userdata, msg: MQTTMessage):
        print(f"[INFO] Received '{msg.payload.decode()}' from '{msg.topic}'")

        applicationID, nodeID, topic = msg.topic.split("/")
        nodeID = int(nodeID)

        payload = msg.payload.decode()

        if topic == "payload":
            decoded_data = json.loads(payload)

            if decoded_data["payloadType"] == "window":
                decoded_data["payloadType"] = f"w{decoded_data['data']['value']}"
                decoded_data["data"]["value"] = decoded_data["data"]["count"]

            sensor_data = Data(
                payloadType=decoded_data["payloadType"],
                nodeID=nodeID,
                canID=decoded_data["data"]["canID"],
                sensorNumber=decoded_data["data"]["sensorNumber"],
                sessionID=decoded_data["data"]["sessionID"],
                readingID=decoded_data["data"]["readingID"],
                value=decoded_data["data"]["value"],
            )

            insert(sensor_data)

        elif topic == "sessions":
            new_sessionID = int(payload)
            create_session_container(new_sessionID)
        else:
            raise ValueError(f"Invalid topic '{topic}'")

    client.on_connect = on_connect
    client.on_message = on_message
