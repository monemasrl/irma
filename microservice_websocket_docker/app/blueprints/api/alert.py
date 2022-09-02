import json

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from ... import socketio
from ...utils.alert import handle_alert

alert_bp = Blueprint("alert", __name__, url_prefix="/alert")


@alert_bp.route("/handle", methods=["POST"])
@jwt_required()
def _handle_alert_route():
    received: dict = json.loads(request.data)

    user_id = get_jwt_identity()["_id"]["$oid"]

    n = handle_alert(received, user_id)

    if n is None:
        return {"message": "Not Found"}, 404

    socketio.emit("change")
    return received
