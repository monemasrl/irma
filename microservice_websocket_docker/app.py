import json
import os
from datetime import datetime, timedelta

import services.database as db
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from flask_mongoengine import MongoEngine
from flask_mqtt import Mqtt
from routes import define_routes
from services.database import user_manager
from services.jwt import init_jwt
from services.mqtt import create_mqtt
from services.scheduler import init_scheduler
from services.socketio import create_socketio

from utils.api_token import api_token_required
from utils.data import to_dashboard_data
from utils.enums import SensorState

# interval for checking sensor timeout
SENSORS_UPDATE_INTERVAL = timedelta(seconds=10)

# for testing purposes
# TODO: move to config file
DISABLE_MQTT = False if os.environ.get("DISABLE_MQTT") != 1 else True


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

    send: dict = to_dashboard_data(
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


def create_app():
    app = Flask(__name__)
    app.config.from_file("./config/config.json", load=json.load)

    socketio = create_socketio(app)
    init_scheduler(app, SENSORS_UPDATE_INTERVAL.total_seconds())
    init_jwt(app)

    database = MongoEngine()
    database.init_app(app)

    CORS(app)

    if not DISABLE_MQTT:
        mqtt: Mqtt = create_mqtt(app)

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

    define_routes(app, socketio, mqtt)

    return app, socketio


if __name__ == "__main__":
    app, socketio = create_app()
    socketio.run(
        app,
        debug=True,
        host="0.0.0.0",
        port=5000,
    )
