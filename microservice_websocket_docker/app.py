import json
import os
from flask import Flask, request, jsonify, render_template_string
from flask_cors import cross_origin, CORS
from flask_mqtt import Mqtt
from flask_mongoengine import MongoEngine
from flask_socketio import SocketIO
from flask_security import Security, MongoEngineUserDatastore, login_required, current_user, login_user
import flask_security
from enum import IntEnum, auto
from os import environ

from datetime import datetime

import iso8601
import requests
import base64

from mobius import utils
from database import microservice

from flask_jwt_extended import create_access_token, get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

# valore teorico della soglia di pericolo del sensore
MAX_TRESHOLD = int(environ.get("MAX_TRESHOLD", 20))

# mobius url
MOBIUS_URL = environ.get("MOBIUS_URL", "http://localhost")
MOBIUS_PORT = environ.get("MOBIUS_PORT", "5002")

# for testing purposes
DISABLE_MQTT = False if environ.get("DISABLE_MQTT") != 1 else True

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
        'db': 'irma',
        'host': 'mongodb://mongo:27017/irma'
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

def decode_data(encoded_data: str) -> dict:
    raw_bytes = base64.b64decode(encoded_data)

    return {
        "payloadType": int.from_bytes(raw_bytes[:1], 'big'),
        "sensorData": int.from_bytes(raw_bytes[1:5], 'big'),
        "mobius_sensorId": raw_bytes[5:15].decode(),
        "mobius_sensorPath": raw_bytes[15:].decode()
    }


def encode_mqtt_data(command: int, iso_timestamp: str) -> bytes:
    encoded_data = b''
    encoded_data += command.to_bytes(1, 'big')
    encoded_data += iso_timestamp.encode()
    
    return base64.b64encode(encoded_data)


# Creazione payload per irma-ui
def to_irma_ui_data(
        sensorID: str,
        sensorName: str,
        applicationID: str,
        state: str,
        titolo1: str,
        titolo2: str,
        titolo3: str,
        dato1: float,
        dato2: float,
        dato3: int,
        unconfirmedAlertIDs: list = []
    ) -> dict:

    return {
        "sensorID": sensorID,
        "sensorName": sensorName,
        "applicationID": applicationID,
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
        "unconfirmedAlertIDs": unconfirmedAlertIDs
    }


class SensorState(IntEnum):
    ERROR=0
    READY=auto()
    RUNNING=auto()
    ALERT_READY=auto()
    ALERT_RUNNING=auto()

    @classmethod
    def to_irma_ui_state(cls, n: int) -> str:
        if n == 0:
            return 'off'
        elif n == 1:
            return 'ok'
        elif n == 2:
            return 'rec'
        elif n >= 3:
            return 'alert'
        else:
            return 'undefined'


class PayloadType(IntEnum):
    READING=0
    START_REC=auto()
    END_REC=auto()
    KEEP_ALIVE=auto()
    CONFIRM=auto()


def update_state(current_state: SensorState, typ: PayloadType, dato: int = 0):
    if current_state == SensorState.ERROR:
        if typ == PayloadType.KEEP_ALIVE:
            return SensorState.READY

    elif current_state == SensorState.READY:
        if typ == PayloadType.START_REC:
            return SensorState.RUNNING
        elif typ == PayloadType.READING:
            if dato >= MAX_TRESHOLD:
                return SensorState.ALERT_READY

    elif current_state == SensorState.RUNNING:
        if typ == PayloadType.READING:
            if dato >= MAX_TRESHOLD:
                return SensorState.ALERT_RUNNING
        elif typ == PayloadType.END_REC:
            return SensorState.READY

    elif current_state == SensorState.ALERT_RUNNING:
        if typ == PayloadType.CONFIRM:
            return SensorState.RUNNING
        elif typ == PayloadType.END_REC:
            return SensorState.ALERT_READY

    elif current_state == SensorState.ALERT_READY:
        if typ == PayloadType.CONFIRM:
            return SensorState.READY

    return current_state


def get_data(sensorID: str) -> dict:
    total_sum: int = 0
    monthly_sum: int = 0

    total_count: int = 0
    monthly_count: int = 0

    total_average: float = 0.0
    monthly_average: float = 0.0

    #salvataggio del valore attuale del mese per il confronto
    current_month: int = datetime.now().month 

    sensor = microservice.Sensor.objects(sensorID=sensorID).first() # type: ignore

    if sensor is None:
        return {}

    state: SensorState = sensor["state"]
    sensorName: str = sensor["sensorName"]
    applicationID: str = str(sensor["application"]["id"])

    collect = microservice.Reading.objects(sensor=sensor).order_by("-publishedAt") # type: ignore

    unconfirmedAlerts = microservice.Alert.objects(
        sensor=sensor,
        isConfirmed=False
    )

    unconfirmedAlertIDs = [str(x["id"]) for x in unconfirmedAlerts]

    for x in collect:
        for data in x["data"]:
            sensor_data: int = data['sensorData']
            read_time: datetime = data['publishedAt']
            read_month: int = read_time.month

            total_sum += sensor_data
            total_count += 1

            if read_month == current_month:
                monthly_sum += sensor_data
                monthly_count += 1

            total_average = total_sum / total_count

            if monthly_count != 0:
                monthly_average = monthly_sum / monthly_count

    send: dict = to_irma_ui_data(
        sensorID=sensorID,
        sensorName=sensorName,
        applicationID=applicationID,
        state=SensorState.to_irma_ui_state(state),
        titolo1="Media Letture Totali",
        dato1=round(total_average, 3),
        titolo2="Media Letture Mensili",
        dato2=round(monthly_average, 3),
        titolo3="Letture eseguite nel mese",
        dato3=monthly_count,
        unconfirmedAlertIDs=unconfirmedAlertIDs
    )

    app.logger.info(f'{send=}')

    return send


def create_socketio(app: Flask):
    # TODO: remove wildcard ?
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

    db = MongoEngine()
    db.init_app(app)

    CORS(app)

    jwt = JWTManager(app)
    if not DISABLE_MQTT:
        mqtt: Mqtt = create_mqtt(app)

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
        app.logger.info('Creo utente')
        user_datastore.create_user(email='bettarini@monema.it', password='password')

    # Create a route to authenticate your users and return JWTs. The
    # create_access_token() function is used to actually generate the JWT.
    @app.route("/api/authenticate", methods=["POST"])
    def custom_login():
        username = request.json.get("username", None)
        password = request.json.get("password", None)

        user = user_datastore.find_user(email=username)

        if flask_security.verify_password(password, user['password']):
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
        sensorIDs: list = json.loads(request.data)["paths"]
        data: list[dict] = [get_data(x) for x in sensorIDs]

        # Filtro via i dati vuoti (sensorID non valido)
        return jsonify(data=[x for x in data if x])

    @app.route('/api/organizations')
    @jwt_required()
    def get_organizations():
        organizations = microservice.Organization.objects() # type: ignore

        if len(organizations) == 0:
            return { 'message': 'Not Found' }, 404

        return jsonify(organizations=organizations)

    @app.route('/api/organizations', methods=['POST'])
    @jwt_required()
    def create_organization():
        record: dict = json.loads(request.data)

        organization = microservice.Organization(organizationName=record['name'])
        organization.save()

        return jsonify(organization.to_json())

    @app.route('/api/applications/<organizationID>', methods=['POST'])
    @jwt_required()
    def create_application(organizationID):
        record: dict = json.loads(request.data)

        organizations = microservice.Organization.objects(id=organizationID) # type: ignore

        if len(organizations) > 0: 
            organization = organizations[0]
            application = microservice.Application(applicationName=record['name'], organization=organization)
            application.save()
            return application.to_json()
        else:
            return { 'message': 'Not Found' }, 404




    @app.route('/api/applications')
    @jwt_required()
    def get_applications():
        organizationID: str = request.args.get('organizationID', '')

        if organizationID == "":
            return { 'message': 'Bad Request' }, 400

        applications = microservice.Application.objects(organization=organizationID) # type: ignore

        if len(applications) == 0:
            return { 'message': 'Not Found' }, 404

        return jsonify(applications=applications)

    @app.route('/api/sensors')
    @jwt_required()
    def get_sensors():
        applicationID: str = request.args.get('applicationID', '')

        if applicationID == "":
            return { 'message': 'Bad Request' }, 400

        sensors = microservice.Sensor.objects(application=applicationID) # type: ignore

        if len(sensors) == 0:
            return { 'message': 'Not Found' }, 404

        return jsonify(sensors=sensors)

    @app.route('/api/<applicationID>/<sensorID>/publish', methods=['POST'])
    def create_record(applicationID: str, sensorID: int):
        # TODO: controllo header token

        app.logger.info(f'{request=}')
        app.logger.info(f'{vars(request)=}')

        data = request.data.decode()
        # record: dict = json.loads(request.data.decode())

        app.logger.info(f'{data=}')
        record: dict = json.loads(data)

        record["data"] = decode_data(record["data"])

        # Vero se arriva da chirpstack
        if "txInfo" in record:
            # TODO: portare a payload di node/app.py
            pass 
            
        application = microservice.Application.objects(id=applicationID).first() # type: ignore

        if application is None:
            app.logger.info(f'Not found')
            return { 'message': 'Not Found' }, 404

        sensor =  microservice.Sensor.objects(sensorID=sensorID).first() # type: ignore


        if sensor is None:
            sensor = microservice.Sensor(
                sensorID=record["sensorID"],
                application=application,
                organization=application["organization"],
                sensorName=record["sensorName"],
                state=SensorState.READY
            )
            sensor.save()

        if record["data"]["payloadType"] == PayloadType.READING:

            if MOBIUS_URL != "":
                app.logger.info(f'Sending to mobius: {record=}')
                utils.insert(record)

            requestedAt = iso8601.parse_date(record["requestedAt"])
            reading = microservice.Reading.objects(requestedAt=requestedAt).first()

            data = microservice.Data(
                payloadType=record['data']['payloadType'],
                sensorData=record['data']['sensorData'],
                publishedAt=iso8601.parse_date(record['publishedAt']),
                mobius_sensorId=record['data']['mobius_sensorId'],
                mobius_sensorPath=record['data']['mobius_sensorPath'],
            )

            if reading is None:
                reading = microservice.Reading(
                    sensor=sensor,
                    requestedAt=requestedAt,
                    data=[data],
                )
            else:
                reading["data"].append(data)


            reading.save()

            if data["sensorData"] >= MAX_TRESHOLD:
                alert = microservice.Alert(
                    reading=reading,
                    sensor=sensor,
                    isConfirmed=False
                )
                alert.save()

        sensor["state"] = update_state(
            sensor["state"], 
            record["data"]["payloadType"],
            record["data"]['sensorData']
        )
        sensor.save()


        socketio.emit('change')
        return record


    @app.route('/api/alert/confirm', methods=['POST'])
    @jwt_required()
    def confirm_alert():
        received: dict = json.loads(request.data)

        alertID = received["alertID"]
        alert = microservice.Alert.objects(id=alertID).first()
        if alert is None:
            return { 'Message': 'Not Found' }, 404

        sensor = alert["sensor"]

        user_id = get_jwt_identity()["_id"]["$oid"]

        user = microservice.User.objects(id=user_id).first()
        
        alert["isConfirmed"] = True
        alert["confirmedBy"] = user
        alert["confirmNote"] = received["confirmNote"]
        alert["confirmTime"] = datetime.now()
        alert.save()

        if microservice.Alert.objects(
            sensor=sensor,
            isConfirmed=False
        ).first() is None:

            sensor["state"] = update_state(
                sensor["state"], 
                PayloadType.CONFIRM
            )
            sensor.save()
    
        socketio.emit('change')
        return received

    @app.route('/api/command', methods=['POST'])
    @jwt_required()
    def sendMqtt(): # alla ricezione di un post pubblica un messaggio sul topic
        received: dict = json.loads(request.data)

        applicationID = received["applicationID"]
        sensorID = received["sensorID"]

        if applicationID == "" or sensorID == "":
            return { 'Message': 'Bad Request' }, 400

        topic: str = f'{applicationID}/{sensorID}/command'

        data: bytes = encode_mqtt_data(received["command"], datetime.now().isoformat())

        if not DISABLE_MQTT:
            mqtt.publish(topic, data)

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
