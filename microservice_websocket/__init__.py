import json
from flask import Flask, request, jsonify
from flask_cors import cross_origin, CORS
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from flask_api import status
from enum import Enum, auto

from datetime import datetime

import iso8601
import requests

from .data_conversion import to_irma_ui_data, to_mobius_payload, decode_devEUI

rec=""

# valore teorico della soglia di pericolo del sensore
MAX_TRESHOLD = 20

# lista dei SENSOR_PATH per effettuare le query a mobius
SENSOR_PATHS = [ "283923423" ]

# mobius url
MOBIUS_URL = "http://localhost:5002"

# for testing purposes
DISABLE_MQTT = False


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
        # Querying mobius for sensor_path
        response: requests.Response = requests.get(f"{MOBIUS_URL}/{sensor_path}")
        decoded_response: dict = json.loads(response.content)

        collect: list[dict] = decoded_response["m2m:rsp"]["m2m:cin"] \
                              if status.is_success(response.status_code) \
                              else []
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

        data: list[dict] = [get_data(x, rec) for x in SENSOR_PATHS]
        socketio.send(jsonify(data=data))

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
    socketio = create_socketio(app)

    # TODO: randomize key gen
    app.config['SECRET_KEY'] = 'secret!'

    ###########################################################################################
    #####configurazione dei dati relativi al cors per la connessione da una pagina esterna#####
    ###########################################################################################
    app.config['CORS_SETTINGS'] = {
        'Content-Type':'application/json',
        'Access-Control-Allow-Origin': 'http://localhost:3000',
        'Access-Control-Allow-Credentials': 'true'
    }
    CORS(app)

    ################################################################
    #####configurazione dei dati relativi alla connessione MQTT#####
    ################################################################
    app.config['MQTT_BROKER_URL'] = 'localhost'
    app.config['MQTT_BROKER_PORT'] = 1883
    app.config['MQTT_TLS_ENABLED'] = False

    if not DISABLE_MQTT:
        mqtt: Mqtt = create_mqtt(app)

    @app.route('/', methods=['GET'])
    @cross_origin()
    def home():
        data: list[dict] = [get_data(x, rec) for x in SENSOR_PATHS]
        return jsonify(data=data)

    @app.route('/', methods=['POST'])
    def create_record():
        global rec
        record: dict = json.loads(request.data)

        # filtraggio degli eventi mandati dall'application server 
        # in modo da non inserire nel database valori irrilevanti
        if "confirmedUplink" in record:
            mobius_payload: dict = to_mobius_payload(record)

            # For testing purposes
            if MOBIUS_URL != "":
                requests.post(f"{MOBIUS_URL}/{record['tags']['sensor_path']}", json=mobius_payload)

            if rec == record['tags']['sensorId']:
                rec = ""

            socketio.emit('change')
            print(f"[DEBUG] Posted payload to '{MOBIUS_URL}'")
            return jsonify(mobius_payload)

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

