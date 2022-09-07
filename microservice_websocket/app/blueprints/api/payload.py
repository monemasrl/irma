import json

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from ... import socketio
from ...utils.api_token import api_token_required
from ...utils.exceptions import ObjectNotFoundException
from ...utils.payload import get_readings, publish, send_mqtt_command

payload_bp = Blueprint("payload", __name__, url_prefix="/payload")


@payload_bp.route("/publish", methods=["POST"])
@api_token_required
def _publish_route():
    data = request.data.decode()

    record: dict = json.loads(data)

    try:
        publish(record)
    except ObjectNotFoundException:
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
def get_readings_route():
    nodeIDs: list = json.loads(request.data)["IDs"]

    readings = get_readings(nodeIDs)

    return jsonify(readings=readings)
