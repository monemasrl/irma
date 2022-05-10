import random
import time

from paho.mqtt import client as mqtt_client


broker = 'localhost'
port = 1883
topic = "application/5/device/2232330000888802/command/down"
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = 'irma'
password = 'irma'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client):
    msg_count = 0
    while True:
        time.sleep(1)  
        result = client.publish(topic, '{"confirmed": false, "fPort": 2, "data": "U3RvcA=="}')#Stops the reading process of the end-device
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send  to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")


def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)


if __name__ == '__main__':
    run()
