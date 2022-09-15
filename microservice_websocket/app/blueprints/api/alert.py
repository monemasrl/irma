import json

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from ... import socketio
from ...utils.alert import handle_alert
from ...utils.exceptions import ObjectNotFoundException

alert_bp = Blueprint("alert", __name__, url_prefix="/alert")


@alert_bp.route("/handle", methods=["POST"])
@jwt_required()
def _handle_alert_route():
    received: dict = json.loads(request.data)

    user_id = get_jwt_identity()["_id"]["$oid"]

    try:
        handle_alert(received, user_id)
    except ObjectNotFoundException:
        return {"message": "not found"}, 404

    socketio.emit("change")
    socketio.emit("change-reading")
    return received
