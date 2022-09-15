from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from ...utils.exceptions import ObjectNotFoundException
from ...utils.session import get_session, get_sessions_id

session_bp = Blueprint("session", __name__, url_prefix="/session")


@session_bp.route("/", methods=["GET"])
@jwt_required()
def get_reading_session():
    nodeID = int(request.args.get("nodeID", "-1"))
    sessionID = int(request.args.get("sessionID", "-1"))

    if nodeID == -1:
        return {"message": "Bad Request"}, 400

    try:
        readings = get_session(nodeID, sessionID)
    except ObjectNotFoundException:
        return {"message", "Not Found"}, 404

    return jsonify(readings=readings)


@session_bp.route("/ids", methods=["GET"])
@jwt_required()
def get_sessions_id_route():
    nodeID = int(request.args.get("nodeID", "-1"))

    if nodeID == -1:
        return {"message": "Bad Request"}, 400

    try:
        sessions_id = get_sessions_id(nodeID)
    except ObjectNotFoundException:
        return {"message", "Not Found"}, 404

    return jsonify(IDs=sessions_id)
