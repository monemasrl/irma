import json
from socket import SocketIO

from flask import Flask, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_mqtt import Mqtt
from services.database import Sensor

from utils.alert import handle_alert
from utils.api_token import api_token_required
from utils.application import create_application, get_applications
from utils.organization import create_organization, get_organizations
from utils.payload import publish, send_mqtt_command
from utils.sensor import get_sensors, update_state


def define_routes(app: Flask, socketio: SocketIO, mqtt: Mqtt):
    _define_organizations_routes(app)
    _define_applications_routes(app)
    _define_sensors_routes(app)
    _define_payload_routes(app, socketio, mqtt)
    _define_alert_routes(app, socketio)
    _define_other_routes(app, socketio)


def _define_organizations_routes(app: Flask):
    @app.route("/api/organizations", methods=["GET"])
    @jwt_required()
    def _get_organizations_route():
        organizations = get_organizations()

        if len(organizations) == 0:
            return {"message": "Not Found"}, 404

        return jsonify(organizations=organizations)

    @app.route("/api/organizations", methods=["POST"])
    @jwt_required()
    def _create_organization_route():
        record: dict = json.loads(request.data)

        organization = create_organization(record["name"])

        return organization.to_json()


def _define_applications_routes(app: Flask):
    @app.route("/api/applications/<organizationID>", methods=["POST"])
    @jwt_required()
    def _create_application_route(organizationID):
        record: dict = json.loads(request.data)

        application = create_application(organizationID, record["name"])

        if application is None:
            return {"message": "Not Found"}, 404

        return application.to_json()

    @app.route("/api/applications", methods=["GET"])
    @jwt_required()
    def _get_applications_route():
        organizationID: str = request.args.get("organizationID", "")

        if organizationID == "":
            return {"message": "Bad Request"}, 400

        applications = get_applications(organizationID)

        if len(applications) == 0:
            return {"message": "Not Found"}, 404

        return jsonify(applications=applications)


def _define_sensors_routes(app: Flask):
    @app.route("/api/sensors", methods=["GET"])
    @jwt_required()
    def _get_sensors_route():
        applicationID: str = request.args.get("applicationID", "")

        if applicationID == "":
            return {"message": "Bad Request"}, 400

        sensors = get_sensors(applicationID)

        if len(sensors) == 0:
            return {"message": "Not Found"}, 404

        return jsonify(sensors=sensors)


def _define_payload_routes(app: Flask, socketio: SocketIO, mqtt: Mqtt):
    @app.route("/api/<applicationID>/<sensorID>/publish", methods=["POST"])
    @api_token_required
    def _publish_route(applicationID: str, sensorID: int):
        data = request.data.decode()

        record: dict = json.loads(data)

        n = publish(applicationID, sensorID, record)

        if n is None:
            app.logger.info("Not found")
            return {"message": "Not Found"}, 404

        socketio.emit("change")
        return record

    @app.route("/api/command", methods=["POST"])
    @jwt_required()
    def _send_mqtt_command_route():
        received: dict = json.loads(request.data)

        applicationID = received.get("applicationID", None)
        sensorID = received.get("sensorID", None)

        if applicationID is None or sensorID is None:
            return {"message": "Bad Request"}, 400

        send_mqtt_command(mqtt, applicationID, sensorID, received["command"])

        print(received)
        return received


def _define_alert_routes(app: Flask, socketio: SocketIO):
    @app.route("/api/alert/handle", methods=["POST"])
    @jwt_required()
    def _handle_alert_route():
        received: dict = json.loads(request.data)

        user_id = get_jwt_identity()["_id"]["$oid"]

        n = handle_alert(received, user_id)

        if n is None:
            return {"message": "Not Found"}, 404

        socketio.emit("change")
        return received


def _define_other_routes(app: Flask, socketio: SocketIO):
    @app.route("/api/check")
    def _check_for_updates():
        sensors = Sensor.objects()

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
