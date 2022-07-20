import json
import os
from flask import Flask, request, jsonify, render_template_string
from flask_cors import cross_origin, CORS
from flask_mqtt import Mqtt
from flask_mongoengine import MongoEngine
from flask_socketio import SocketIO
from flask_security import Security, MongoEngineUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user, verify_password, login_user
from enum import Enum, auto
from os import environ

from datetime import datetime

import iso8601
import requests
import base64

from mobius import utils
from database import microservice

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

rec=""

# valore teorico della soglia di pericolo del sensore
MAX_TRESHOLD = int(environ.get("MAX_TRESHOLD", 20))

# mobius url
MOBIUS_URL = environ.get("MOBIUS_URL", "http://localhost")
MOBIUS_PORT = environ.get("MOBIUS_PORT", "5002")

# for testing purposes
DISABLE_MQTT = False if environ.get("DISABLE_MQTT") != 1 else True

cached_sensor_paths = []

# Class-based application configuration
class ConfigClass(object):
    """ Flask application config """

    # Generate a nice key using secrets.token_urlsafe()
    SECRET_KEY = os.environ.get("SECRET_KEY", 'pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw')
    # Bcrypt is set as default SECURITY_PASSWORD_HASH, which requires a salt
    # Generate a good salt using: secrets.SystemRandom().getrandbits(128)
    SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT", '146585145368132386173505678016728509634')

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", 'pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw')
    # Flask-MongoEngine settings
    MONGODB_SETTINGS = {
        'db': 'mobius',
        'host': 'mongodb://mongo:27017/mobius'
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
    MQTT_BROKER_URL = environ.get("MQTT_BROKER_URL", 'localhost')
    MQTT_BROKER_PORT = int(environ.get("MQTT_BROKER_PORT", 1883))
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
        collect: list[dict] = utils.read(sensor_path)
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

    jwt = JWTManager(app)
    if not DISABLE_MQTT:
        mqtt: Mqtt = create_mqtt(app)

    db = MongoEngine()
    db.init_app(app)

    user_datastore = MongoEngineUserDatastore(db, microservice.User, microservice.Role)
    security = Security(app, user_datastore)

    # Register a callback function that takes whatever object is passed in as the
    # identity when creating JWTs and converts it to a JSON serializable format.
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        app.logger.info(f'{user=}')
        return user_datastore.find_user(email=user.email)

    # Register a callback function that loads a user from your database whenever
    # a protected route is accessed. This should return any python object on a
    # successful lookup, or None if the lookup failed for any reason (for example
    # if the user has been deleted from the database).
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        app.logger.info(f'{identity=}')
        return user_datastore.find_user(email=identity['email'])

    # Create a user to test with
    @app.before_first_request
    def create_user():
        user_datastore.create_user(email='bettarini@monema.it', password='password')

    # Create a route to authenticate your users and return JWTs. The
    # create_access_token() function is used to actually generate the JWT.
    # @app.route("/authenticate", methods=["POST"])
    # def login():
    #     username = request.json.get("username", None)
    #     password = request.json.get("password", None)

    #     user = user_datastore.find_user(email=username)

    #     if not user or not user.check_password(password):
    #         return jsonify("Wrong username or password"), 401
    #     if username != "test" or password != "test":
    #         return jsonify({"msg": "Bad username or password"}), 401

    #     access_token = create_access_token(identity=username)
    #     return jsonify(access_token=access_token)
    @app.route("/api/authenticate", methods=["POST"])
    def custom_login():
        username = request.json.get("username", None)
        password = request.json.get("password", None)

        user = user_datastore.find_user(email=username)

        if verify_password(password, user['password']):
            login_user(user=user, remember=False)
            access_token = create_access_token(identity=current_user)
            return jsonify(access_token=access_token)

        return jsonify("Wrong username or password"), 401

    @app.route("/api/jwttest")
    @jwt_required()
    def jwttest():
        """View protected by jwt test. If necessary, exempt it from csrf protection. See flask_wtf.csrf for more info"""
        return jsonify({"foo": "bar", "baz": "qux"})

    # Views
    @app.route('/')
    @login_required
    def webhome():
        return render_template_string("Hello {{ current_user.email }}")

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
