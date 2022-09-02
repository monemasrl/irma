import json

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required

from ... import socketio
from ...utils.api_token import api_token_required
from ...utils.data import fetch_data
from ...utils.payload import publish, send_mqtt_command

payload_bp = Blueprint("payload", __name__, url_prefix="/payload")


@payload_bp.route("/publish", methods=["POST"])
@api_token_required
def _publish_route():
    data = request.data.decode()

    record: dict = json.loads(data)

    applicationID: str = record["applicationID"]
    sensorID: str = record["sensorID"]

    n = publish(applicationID, sensorID, record)

    if n is None:
        current_app.logger.info("Not found")
        return {"message": "Not Found"}, 404

    socketio.emit("change")
    return record


@payload_bp.route("/command", methods=["POST"])
@jwt_required()
def _send_mqtt_command_route():
    received: dict = json.loads(request.data)

    applicationID = received.get("applicationID", None)
    sensorID = received.get("sensorID", None)

    if applicationID is None or sensorID is None:
        return {"message": "Bad Request"}, 400

    send_mqtt_command(applicationID, sensorID, received["command"])

    print(received)
    return received


@payload_bp.route("/", methods=["POST"])
def fetch_data_route():
    sensorIDs: list = json.loads(request.data)["IDs"]
    data: list[dict] = [fetch_data(x) for x in sensorIDs]

    # Filtro via i dati vuoti (sensorID non valido)
    return jsonify(readings=[x for x in data if x])
