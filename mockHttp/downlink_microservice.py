
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from google.protobuf.json_format import Parse

import json
from flask import Flask, request, jsonify, Response
from flask_mqtt import Mqtt

app = Flask(__name__)

app.config['MQTT_BROKER_URL'] = 'localhost'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_TLS_ENABLED'] = False


mqtt = Mqtt(app)

@mqtt.on_connect() # connessione al topic mqtt
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('application/5/device/2232330000888802/command/down')

@mqtt.on_message() # preparazione del messaggio da pubblicare sul topic
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )

@app.route('/', methods=['GET'])
def home():
    return "<html><head><title>downlink_microservice</title></head><body><div>Script di invio messaggi MQTT per l'avvio dei comandi Start e Stop degli end-device</div></body></html>"


@app.route('/', methods=['POST'])
def sendMqtt(): # alla ricezione di un post pubblica un messaggio sul topic
    option=request.data
    if option == 1:
        data=json.dumps({'confirmed': False, 'fPort': 2, 'data': 'U3RhcnQ='})
    else:
        data=json.dumps({'confirmed': False, 'fPort': 2, 'data': 'U3RvcA=='})
    mqtt.publish('application/5/device/2232330000888802/command/down', data)
    return option

if __name__ == "__main__":
    app.run(port = 5001,debug = True)
