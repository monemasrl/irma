
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from google.protobuf.json_format import Parse

import json
from flask import Flask, request, jsonify, Response
from flask_mqtt import Mqtt

from flask_cors import CORS, cross_origin

app = Flask(__name__)

###########################################################################################
#####configurazione dei dati relativi al cors per la connessione da una pagina esterna#####
###########################################################################################
app.config['CORS_SETTINGS']= {
    'Content-Type':'application/json',
    'Access-Control-Allow-Origin': 'http://localhost:3000',
    'Access-Control-Allow-Credentials': 'true'
}

################################################################
#####configurazione dei dati relativi alla connessione MQTT#####
################################################################
app.config['MQTT_BROKER_URL'] = 'localhost'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_TLS_ENABLED'] = False

CORS(app)
mqtt = Mqtt(app)

@mqtt.on_connect() # connessione al topic mqtt
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('application')

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
    received=json.loads(request.data)
    appNum=str(received['app']['code']) # application ID ricevuto per identificare le varie app sull'application server
    devEUI=str(received['app']['eui']) # devEUI rivuto per identificare i dipositivi nelle varie app
    if received['statoStaker'] == 1: 
        data=json.dumps({'confirmed': False, 'fPort': 2, 'data': 'U3RhcnQ='}) # comando Start
    else:
        data=json.dumps({'confirmed': False, 'fPort': 2, 'data': 'U3RvcA=='}) # comando Stop
    topic='application/'+appNum+'/device/'+devEUI+'/command/down'
    mqtt.publish(topic, data)
    print(received)
    return received

if __name__ == "__main__":
    app.run(port = 5001,debug = True)
