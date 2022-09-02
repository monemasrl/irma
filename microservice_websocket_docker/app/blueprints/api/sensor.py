from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from ...utils.sensor import get_sensors

sensor_bp = Blueprint("sensor", __name__, url_prefix="/sensors")


@sensor_bp.route("/", methods=["GET"])
@jwt_required()
def _get_sensors_route():
    applicationID: str = request.args.get("applicationID", "")

    if applicationID == "":
        return {"message": "Bad Request"}, 400

    sensors = get_sensors(applicationID)

    if len(sensors) == 0:
        return {"message": "Not Found"}, 404

    return jsonify(sensors=sensors)
