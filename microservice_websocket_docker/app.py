import base64
import json
import os
from datetime import datetime, timedelta
from enum import IntEnum, auto
from functools import wraps

import database as db
import iso8601
import requests
from database import user_manager
from flask import Flask, jsonify, make_response, request
from flask_apscheduler import APScheduler
from flask_cors import CORS, cross_origin
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from flask_mongoengine import MongoEngine
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from mobius import utils

# valore teorico della soglia di pericolo del sensore
MAX_TRESHOLD = int(os.environ.get("MAX_TRESHOLD", 20))

# mobius url
MOBIUS_URL = os.environ.get("MOBIUS_URL", "http://localhost")
MOBIUS_PORT = os.environ.get("MOBIUS_PORT", "5002")

# for testing purposes
DISABLE_MQTT = False if os.environ.get("DISABLE_MQTT") != 1 else True

# for sensor timeout
SENSORS_TIMEOUT_INTERVAL = timedelta(seconds=30)

# interval for checking sensor timeout
SENSORS_UPDATE_INTERVAL = timedelta(seconds=10)


# Class-based application configuration
class ConfigClass(object):
    """Flask application config"""

    # Generate a nice key using secrets.token_urlsafe()
    SECRET_KEY = os.environ.get(
        "SECRET_KEY", "pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw"
    )

    # JWT SETTINGS
    JWT_SECRET_KEY = os.environ.get(
        "JWT_SECRET_KEY", "pf9Wkove4IKEAXvy-cQkeDPhv9Cb3Ag-wyJILbq_dFw"
    )
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(weeks=1)

    # Flask-MongoEngine settings
    MONGODB_SETTINGS = {"db": "irma", "host": "mongodb://mongo:27017/irma"}

    # Flask-User settings
    USER_APP_NAME = (
        "Flask-User MongoDB App"  # Shown in and email templates and page footers
    )
    USER_ENABLE_EMAIL = False  # Disable email authentication
    USER_ENABLE_USERNAME = True  # Enable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = False  # Simplify register form

    #####################################################################################
    # configurazione dei dati relativi al cors per la connessione da una pagina esterna #
    #####################################################################################
    CORS_SETTINGS = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Credentials": "true",
    }

    ##########################################################
    # configurazione dei dati relativi alla connessione MQTT #
    ##########################################################
    MQTT_BROKER_URL = os.environ.get("MQTT_BROKER_URL", "localhost")
    MQTT_BROKER_PORT = int(os.environ.get("MQTT_BROKER_PORT", 1883))
    MQTT_TLS_ENABLED = False

    ##############
    # APS Config #
    ##############

    SCHEDULER_API_ENABLED = True


def api_token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if "Authorization" not in request.headers:
            return make_response(jsonify({"message": "No API Token Provided"}), 401)

        token: str = request.headers["Authorization"].split(" ")[1]

        with open("./api-tokens.txt", "r") as file:
            tokens: list[str] = [x.strip() for x in file.readlines()]

            if token not in tokens:
                return make_response(jsonify({"message": "Invalid Token"}), 401)

        return f(*args, **kwargs)

    return decorator


def decode_data(encoded_data: str) -> dict:
    raw_bytes = base64.b64decode(encoded_data)

    return {
        "payloadType": int.from_bytes(raw_bytes[:1], "big"),
        "sensorData": int.from_bytes(raw_bytes[1:5], "big"),
        "mobius_sensorId": raw_bytes[5:15].decode().strip(),
        "mobius_sensorPath": raw_bytes[15:].decode().strip(),
    }


def encode_mqtt_data(command: int, iso_timestamp: str) -> bytes:
    encoded_data = b""
    encoded_data += command.to_bytes(1, "big")
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
    unhandledAlertIDs: list,
) -> dict:

    return {
        "sensorID": sensorID,
        "sensorName": sensorName,
        "applicationID": applicationID,
        "state": state,
        "datiInterni": [
            {"titolo": titolo1, "dato": dato1},
            {"titolo": titolo2, "dato": dato2},
            {"titolo": titolo3, "dato": dato3},
        ],
        "unhandledAlertIDs": unhandledAlertIDs,
    }


class SensorState(IntEnum):
    ERROR = 0
    READY = auto()
    RUNNING = auto()
    ALERT_READY = auto()
    ALERT_RUNNING = auto()

    @classmethod
    def to_irma_ui_state(cls, n: int) -> str:
        if n == 0:
            return "off"
        elif n == 1:
            return "ok"
        elif n == 2:
            return "rec"
        elif n >= 3:
            return "alert"
        else:
            return "undefined"


class PayloadType(IntEnum):
    READING = 0
    START_REC = auto()
    END_REC = auto()
    KEEP_ALIVE = auto()
    HANDLE_ALERT = auto()


def update_state(
    current_state: SensorState,
    lastSeenAt: datetime,
    typ: PayloadType | None = None,
    dato: int = 0,
):

    is_timed_out: bool = (datetime.now() - lastSeenAt) > SENSORS_TIMEOUT_INTERVAL

    if current_state == SensorState.ERROR:
        if typ == PayloadType.KEEP_ALIVE:
            return SensorState.READY

    elif current_state == SensorState.READY:
        if typ == PayloadType.START_REC:
            return SensorState.RUNNING
        elif typ == PayloadType.READING:
            if dato >= MAX_TRESHOLD:
                return SensorState.ALERT_READY
        elif is_timed_out:
            return SensorState.ERROR

    elif current_state == SensorState.RUNNING:
        if typ == PayloadType.READING:
            if dato >= MAX_TRESHOLD:
                return SensorState.ALERT_RUNNING
        elif typ == PayloadType.END_REC:
            return SensorState.READY

    elif current_state == SensorState.ALERT_RUNNING:
        if typ == PayloadType.HANDLE_ALERT:
            return SensorState.RUNNING
        elif typ == PayloadType.END_REC:
            return SensorState.ALERT_READY

    elif current_state == SensorState.ALERT_READY:
        if typ == PayloadType.HANDLE_ALERT:
            if is_timed_out:
                return SensorState.ERROR
            else:
                return SensorState.READY

    return current_state


def get_data(sensorID: str) -> dict:
    total_sum: int = 0
    monthly_sum: int = 0

    total_count: int = 0
    monthly_count: int = 0

    total_average: float = 0.0
    monthly_average: float = 0.0

    # salvataggio del valore attuale del mese per il confronto
    current_month: int = datetime.now().month

    sensor = db.Sensor.objects(sensorID=sensorID).first()

    if sensor is None:
        return {}

    state: SensorState = sensor["state"]
    sensorName: str = sensor["sensorName"]
    applicationID: str = str(sensor["application"]["id"])

    collect = db.Reading.objects(sensor=sensor).order_by("-publishedAt")

    unhandledAlerts = db.Alert.objects(sensor=sensor, isHandled=False)

    unhandledAlertIDs = [str(x["id"]) for x in unhandledAlerts]

    for x in collect:
        for data in x["data"]:
            sensor_data: int = data["sensorData"]
            read_time: datetime = data["publishedAt"]
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
        unhandledAlertIDs=unhandledAlertIDs,
    )

    app.logger.info(f"{send=}")

    return send


def create_socketio(app: Flask):
    # TODO: remove wildcard ?
    socketio: SocketIO = SocketIO(app, cors_allowed_origins="*")

    @socketio.on("connect")
    def connected():
        print("Connected")

    @socketio.on("disconnect")
    def disconnected():
        print("Disconnected")

    @socketio.on("change")
    def onChange():
        print("Changed")

    return socketio


def create_mqtt(app: Flask) -> Mqtt:
    mqtt = Mqtt(app)

    @mqtt.on_connect()
    def handle_connect(client, userdata, flags, rc):
        mqtt.subscribe("application")

    @mqtt.on_message()
    def handle_mqtt_message(client, userdata, message):
        pass

    return mqtt


def init_scheduler(app: Flask):
    scheduler = APScheduler()
    scheduler.init_app(app)

    @scheduler.task(
        "interval", id="update_state", seconds=SENSORS_UPDATE_INTERVAL.total_seconds()
    )
    def periodically_get_route():
        app.logger.info(
            f"Periodic get every {SENSORS_UPDATE_INTERVAL.total_seconds()} seconds!"
        )
        requests.get("http://localhost:5000/api/check")


def create_app():
    app = Flask(__name__)
    app.config.from_object(__name__ + ".ConfigClass")
    socketio = create_socketio(app)

    databse = MongoEngine()
    databse.init_app(app)

    CORS(app)

    jwt = JWTManager(app)
    if not DISABLE_MQTT:
        mqtt: Mqtt = create_mqtt(app)

    # Register a callback function that takes whatever object is passed in as the
    # identity when creating JWTs and converts it to a JSON serializable format.
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        app.logger.info(f"Looking up: {user=}")
        return user_manager.get_user(user["email"])

    # Register a callback function that loads a user from your database whenever
    # a protected route is accessed. This should return any python object on a
    # successful lookup, or None if the lookup failed for any reason (for example
    # if the user has been deleted from the database).
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        app.logger.info(f"{identity=}")
        return user_manager.get_user(identity["email"])

    # Create a user to test with
    @app.before_first_request
    def create_user():
        app.logger.info("Creo utente")
        user_manager.create_user(email="bettarini@monema.it", password="password")

    # Create a route to authenticate your users and return JWTs. The
    # create_access_token() function is used to actually generate the JWT.
    @app.route("/api/authenticate", methods=["POST"])
    def authenticate():
        json_payload = json.loads(request.data)
        username = json_payload.get("username", None)
        password = json_payload.get("password", None)

        if username is None or password is None:
            return jsonify({"message": "Bad Request"}), 400

        user = user_manager.get_user(username)

        if user is None:
            return jsonify({"message": "User not found"}), 404

        if user_manager.verify(user, password):
            access_token = create_access_token(identity=user)
            refresh_token = create_refresh_token(identity=user)
            return jsonify(access_token=access_token, refresh_token=refresh_token)

        return jsonify({"message": "wrong username or password"}), 401

    @app.route("/api/refresh", methods=["POST"])
    @jwt_required(refresh=True)
    def refresh_token():
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity)
        return jsonify(access_token=access_token)

    @app.route("/api/jwttest")
    @jwt_required()
    def jwttest():
        """
        View protected by jwt test. If necessary, exempt it from csrf protection.
        See flask_wtf.csrf for more info
        """
        return jsonify({"foo": "bar", "baz": "qux"})

    @app.route("/api/api-token-test")
    @api_token_required
    def api_token_test():
        return jsonify({"message": "Valid API Token!"})

    @app.route("/", methods=["POST"])
    @cross_origin()
    def home():
        sensorIDs: list = json.loads(request.data)["IDs"]
        data: list[dict] = [get_data(x) for x in sensorIDs]

        # Filtro via i dati vuoti (sensorID non valido)
        return jsonify(readings=[x for x in data if x])

    @app.route("/api/check")
    def check_for_updates():
        sensors = db.Sensor.objects()

        update_frontend = False

        for sensor in sensors:
            new_state = update_state(sensor["state"], sensor["lastSeenAt"])

            if sensor["state"] != new_state:
                update_frontend = True
                sensor["state"] = new_state
                sensor.save()

        if update_frontend:
            app.logger.info("Detected sensor-state change(s), emitting 'change'")
            socketio.emit("change")

        return jsonify(message=("Changed" if update_frontend else "Not Changed"))

    @app.route("/api/organizations")
    @jwt_required()
    def get_organizations():
        organizations = db.Organization.objects()

        if len(organizations) == 0:
            return {"message": "Not Found"}, 404

        return jsonify(organizations=organizations)

    @app.route("/api/organizations", methods=["POST"])
    @jwt_required()
    def create_organization():
        record: dict = json.loads(request.data)

        organization = db.Organization(organizationName=record["name"])
        organization.save()

        return jsonify(organization.to_json())

    @app.route("/api/applications/<organizationID>", methods=["POST"])
    @jwt_required()
    def create_application(organizationID):
        record: dict = json.loads(request.data)

        organizations = db.Organization.objects(id=organizationID)

        if len(organizations) > 0:
            organization = organizations[0]
            application = db.Application(
                applicationName=record["name"], organization=organization
            )
            application.save()
            return application.to_json()
        else:
            return {"message": "Not Found"}, 404

    @app.route("/api/applications")
    @jwt_required()
    def get_applications():
        organizationID: str = request.args.get("organizationID", "")

        if organizationID == "":
            return {"message": "Bad Request"}, 400

        applications = db.Application.objects(organization=organizationID)

        if len(applications) == 0:
            return {"message": "Not Found"}, 404

        return jsonify(applications=applications)

    @app.route("/api/sensors")
    @jwt_required()
    def get_sensors():
        applicationID: str = request.args.get("applicationID", "")

        if applicationID == "":
            return {"message": "Bad Request"}, 400

        sensors = db.Sensor.objects(application=applicationID)

        if len(sensors) == 0:
            return {"message": "Not Found"}, 404

        return jsonify(sensors=sensors)

    @app.route("/api/<applicationID>/<sensorID>/publish", methods=["POST"])
    @api_token_required
    def create_record(applicationID: str, sensorID: int):
        # TODO: controllo header token

        app.logger.info(f"{request=}")
        app.logger.info(f"{vars(request)=}")

        data = request.data.decode()
        # record: dict = json.loads(request.data.decode())

        app.logger.info(f"{data=}")
        record: dict = json.loads(data)

        record["data"] = decode_data(record["data"])

        # Vero se arriva da chirpstack
        if "txInfo" in record:
            # TODO: portare a payload di node/app.py
            pass

        application = db.Application.objects(id=applicationID).first()

        if application is None:
            app.logger.info("Not found")
            return {"message": "Not Found"}, 404

        sensor = db.Sensor.objects(sensorID=sensorID).first()

        if sensor is None:
            sensor = db.Sensor(
                sensorID=record["sensorID"],
                application=application,
                organization=application["organization"],
                sensorName=record["sensorName"],
                state=SensorState.READY,
                lastSeenAt=datetime.now(),
            )
            sensor.save()

        if record["data"]["payloadType"] == PayloadType.READING:

            if MOBIUS_URL != "":
                app.logger.info(f"Sending to mobius: {record=}")
                utils.insert(record)

            requestedAt = iso8601.parse_date(record["requestedAt"])
            reading = db.Reading.objects(requestedAt=requestedAt).first()

            data = db.Data(
                payloadType=record["data"]["payloadType"],
                sensorData=record["data"]["sensorData"],
                publishedAt=iso8601.parse_date(record["publishedAt"]),
                mobius_sensorId=record["data"]["mobius_sensorId"],
                mobius_sensorPath=record["data"]["mobius_sensorPath"],
            )

            if reading is None:
                reading = db.Reading(
                    sensor=sensor,
                    requestedAt=requestedAt,
                    data=[data],
                )
            else:
                reading["data"].append(data)

            reading.save()

            if data["sensorData"] >= MAX_TRESHOLD:
                alert = db.Alert(reading=reading, sensor=sensor, isHandled=False)
                alert.save()

        sensor["lastSeenAt"] = datetime.now()
        sensor["state"] = update_state(
            sensor["state"],
            sensor["lastSeenAt"],
            record["data"]["payloadType"],
            record["data"]["sensorData"],
        )
        sensor.save()

        socketio.emit("change")
        return record

    @app.route("/api/alert/handle", methods=["POST"])
    @jwt_required()
    def handle_alert():
        received: dict = json.loads(request.data)

        alertID = received["alertID"]
        alert = db.Alert.objects(id=alertID).first()
        if alert is None:
            return {"message": "Not Found"}, 404

        sensor = alert["sensor"]

        user_id = get_jwt_identity()["_id"]["$oid"]

        user = db.User.objects(id=user_id).first()

        alert["isConfirmed"] = received["isConfirmed"]
        alert["isHandled"] = True
        alert["handledBy"] = user
        alert["handledAt"] = datetime.now()
        alert["handleNote"] = received["handleNote"]
        alert.save()

        if db.Alert.objects(sensor=sensor, isHandled=False).first() is None:

            sensor["state"] = update_state(
                sensor["state"], sensor["lastSeenAt"], PayloadType.HANDLE_ALERT
            )
            sensor.save()

        socketio.emit("change")
        return received

    @app.route("/api/command", methods=["POST"])
    @jwt_required()
    def sendMqtt():  # alla ricezione di un post pubblica un messaggio sul topic
        received: dict = json.loads(request.data)

        applicationID = received.get("applicationID", None)
        sensorID = received.get("sensorID", None)

        if applicationID is None or sensorID is None:
            return {"message": "Bad Request"}, 400

        topic: str = f"{applicationID}/{sensorID}/command"

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
