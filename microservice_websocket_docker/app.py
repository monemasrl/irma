import json
from flask import Flask, request, jsonify
from flask_cors import cross_origin, CORS
from flask_mqtt import Mqtt
from flask_mongoengine import MongoEngine
from flask_socketio import SocketIO
from flask_security import Security, MongoEngineUserDatastore, \
    UserMixin, RoleMixin, login_required
from enum import Enum, auto
from os import environ

from datetime import datetime

import iso8601
import requests
import base64
from microservice_websocket_docker.database.microservice import User

from mobius import utils
from database import microservice

rec=""

# valore teorico della soglia di pericolo del sensore
MAX_TRESHOLD = int(environ.get("MAX_TRESHOLD", 20))

# mobius url
MOBIUS_URL = environ.get("MOBIUS_URL", "http://localhost")
MOBIUS_PORT = environ.get("MOBIUS_PORT", "5002")

# for testing purposes
DISABLE_MQTT = False if environ.get("DISABLE_MQTT") != 1 else True

# MQTT 
MQTT_BROKER_URL = environ.get("MQTT_BROKER_URL", 'localhost')
MQTT_BROKER_PORT = int(environ.get("MQTT_BROKER_PORT", 1883))

cached_sensor_paths = []

# Class-based application configuration
class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'

    # Flask-MongoEngine settings
    MONGODB_SETTINGS = {
        'db': 'tst_app',
        'host': 'mongodb://localhost:27017/mobius'
    }

    # Flask-User settings
    USER_APP_NAME = "Flask-User MongoDB App"      # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = False      # Disable email authentication
    USER_ENABLE_USERNAME = True    # Enable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = False    # Simplify register form


    ###########################################################################################
    #####configurazione dei dati relativi al cors per la connessione da una pagina esterna#####
    ###########################################################################################
    CORS_SETTINGS = {
        'Content-Type':'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Credentials': 'true'
    }


    ################################################################
    #####configurazione dei dati relativi alla connessione MQTT#####
    ################################################################
    MQTT_BROKER_URL = MQTT_BROKER_URL
    MQTT_BROKER_PORT = MQTT_BROKER_PORT
    MQTT_TLS_ENABLED = False

def decode_devEUI(encoded_devEUI: str) -> str:
    return base64.b64decode(encoded_devEUI).hex()


# Creazione payload per irma-ui
def to_irma_ui_data(
        devEUI: str,
        applicationID: str,
        sensorId: str,
        state: str,
        titolo1: str,
        titolo2: str,
        titolo3: str,
        dato1: float,
        dato2: float,
        dato3: int,
    ) -> dict:

    return {
        "devEUI": devEUI,
        "applicationID": applicationID,
        "sensorId": sensorId,
        "state": state,
        "datiInterni": [
            {
                "titolo": titolo1,
                "dato": dato1
            },
            {
                "titolo": titolo2,
                "dato": dato2
            },
            {
                "titolo": titolo3,
                "dato": dato3
            },
        ],
    }


class State(Enum):
    OFF=auto()
    OK=auto()
    REC=auto()
    ALERT=auto()


def get_state(dato: int) -> State:
    if dato == 0:
        return State.OFF
    elif dato < MAX_TRESHOLD:
        return State.OK
    return State.ALERT


def get_sensorData(rawData: str) -> int:
    sensorData = json.loads(rawData)['sensorData']
    sensorData = int(sensorData)
    return sensorData


def get_month(rawDateTime: str) -> int:
    month = iso8601.parse_date(rawDateTime).month
    return month


def get_data(sensor_path: str, rec: str) -> dict:
    total_sum: int = 0
    monthly_sum: int = 0

    total_count: int = 0
    monthly_count: int = 0

    total_average: float = 0.0
    monthly_average: float = 0.0

    state: State = State.OFF
    #salvataggio del valore attuale del mese per il confronto
    current_month: int = datetime.now().month 

    # For testing purposes
    if MOBIUS_URL != "":
        collect: list[dict] = utils.read({)
    else:
        collect = []

    for x in collect:
        sensor_data: int = get_sensorData(x['sensorData']['objectJSON'])
        sensorId: str = x['con']['metadata']['sensorId']
        read_time: str = x['con']['metadata']['readingTimestamp']
        read_month: int = get_month(read_time)

        state = State.REC if rec == sensorId else get_state(sensor_data)

        total_sum += sensor_data
        total_count += 1

        if read_month == current_month:
            monthly_sum += sensor_data
            monthly_count += 1

        total_average = total_sum / total_count

        if monthly_count != 0:
            monthly_average = monthly_sum / monthly_count

    if state in [State.OK, State.REC] and len(collect) > 0:
        devEUI: str = collect[-1]['sensorData']['devEUI']
        applicationID: str = collect[-1]['sensorData']['applicationID']
        sensorId: str = collect[-1]['con']['metadata']['sensorId']
    else:
        devEUI: str = ""
        applicationID: str = ""
        sensorId: str = ""

    send: dict = to_irma_ui_data(
        devEUI=devEUI,
        applicationID=applicationID,
        sensorId=sensorId,
        state=state.name.lower(),
        titolo1="Media Letture Totali",
        dato1=round(total_average, 3),
        titolo2="Media Letture Mensili",
        dato2=round(monthly_average, 3),
        titolo3="Letture eseguite nel mese",
        dato3=monthly_count
    )

    return send


def create_socketio(app: Flask):
    # TODO: remove wildcard
    socketio: SocketIO = SocketIO(app, cors_allowed_origins="*")

    @socketio.on('connect')
    def connected():
        print('Connected')

    @socketio.on('disconnect')
    def disconnected():
        print('Disconnected')

    @socketio.on('change')
    def onChange():
        print('Changed')

        if cached_sensor_paths:
            data: list[dict] = [get_data(x, rec) for x in cached_sensor_paths]
            socketio.send(jsonify(data=data))
        else:
            socketio.send(jsonify({}))

    return socketio


def create_mqtt(app: Flask) -> Mqtt:
    mqtt = Mqtt(app)

    @mqtt.on_connect()
    def handle_connect(client, userdata, flags, rc):
        mqtt.subscribe('application')

    @mqtt.on_message()
    def handle_mqtt_message(client, userdata, message):
        data = dict(
            topic=message.topic,
            payload=message.payload.decode()
        )

    return mqtt


def create_app():
    app = Flask(__name__)
    app.config.from_object(__name__+'.ConfigClass')
    socketio = create_socketio(app)

    CORS(app)

    if not DISABLE_MQTT:
        mqtt: Mqtt = create_mqtt(app)

    user_datastore = MongoEngineUserDatastore(db, microservice.User, microservice.Role)
    # The Home page is accessible to anyone

    # Create a user to test with
    @app.before_first_request
    def create_user():
        user_datastore.create_user(email='bettarini@monema.it', password='password')

    # Views
    @app.route('/')
    @login_required
    def home():
        return render_template('index.html')

    @app.route('/', methods=['POST'])
    @cross_origin()
    def home():
        cached_sensor_paths: list = json.loads(request.data)["paths"]
        data: list[dict] = [get_data(x, rec) for x in cached_sensor_paths]
        return jsonify(data=data)

    @app.route('/publish', methods=['POST'])
    def create_record():
        global rec
        record: dict = json.loads(request.data)

        # filtraggio degli eventi mandati dall'application server 
        # in modo da non inserire nel database valori irrilevanti
        if "confirmedUplink" in record:
            # For testing purposes
            if MOBIUS_URL != "":
                mobius_data = utils.insert(record)

            if rec == record['tags']['sensorId']:
                rec = ""

            socketio.emit('change')
            return mobius_data

        print("[DEBUG] Received message different than Uplink")
        rec = record['tags']['sensorId']
        socketio.emit('change')
        return {}

    @app.route('/downlink', methods=['POST'])
    def sendMqtt(): # alla ricezione di un post pubblica un messaggio sul topic
        received: dict = json.loads(request.data)

        # application ID ricevuto per identificare le varie app sull'application server
        applicationID: str = str(received['applicationID'])
        # devEUI rivuto per identificare i dipositivi nelle varie app
        devEUI: str = decode_devEUI(received['devEUI'])

        topic: str = 'application/'+applicationID+'/device/'+devEUI+'/command/down'

        start: str = 'U3RhcnQ='
        stop: str = 'U3RvcA=='

        data: str = json.dumps({
            'confirmed': False,
            'fPort': 2,
            'data': start if received['statoStaker'] == 1 else stop
        })

        if not DISABLE_MQTT:
            mqtt.publish(topic, data.encode())

        print(received)
        return received

    return app, socketio

if __name__ == "__main__":
    app, socketio = create_app()
    socketio.run(
        app,
        debug=True,
        host="0.0.0.0",
        port=5000,
    )
