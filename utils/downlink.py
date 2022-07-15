import random
import time
import json

from paho.mqtt import client as mqtt_client


broker = 'localhost'
port = 1883
topic = "application/5/device/2232330000888802/command/down"  #default topic to schedule a downlink trought MQTT
# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 1000)}'
#username = 'irma'
#password = 'irma'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    #client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client):
    msg_count = 0
    while True:
        time.sleep(1)  
        data=json.dumps({'confirmed': False, 'fPort': 2, 'data': 'U3RhcnQ='})#Start command for end-device
        print("(1) Stop ")
        print("(2) Start ")
        choice=input("Your choice : ")
        if choice=="1":   #If choice is equal to 1 the command will be 'Stop' and in any other case il will be 'Start'
            data=json.dumps({'confirmed': False, 'fPort': 2, 'data': 'U3RvcA=='})#Stop command for end-device
        
        result = client.publish(topic, data)
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
