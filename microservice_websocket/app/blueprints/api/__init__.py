from flask import Blueprint, jsonify, current_app

from .organization import organization_bp
from .application import application_bp
from .node import node_bp
from .payload import payload_bp
from .alert import alert_bp
from .jwt import jwt_bp
from .session import session_bp

from ... import socketio
from ...services.database import Node, user_manager
from ...utils.node import update_state
from ...utils.api_token import api_token_required

bp = Blueprint("api", __name__, url_prefix="/api")

bp.register_blueprint(organization_bp)
bp.register_blueprint(application_bp)
bp.register_blueprint(node_bp)
bp.register_blueprint(payload_bp)
bp.register_blueprint(alert_bp)
bp.register_blueprint(jwt_bp)
bp.register_blueprint(session_bp)


@bp.route("/check")
def _check_for_updates():
    nodes = Node.objects()

    update_frontend = False

    for node in nodes:
        new_state = update_state(node["state"], node["lastSeenAt"])

        if node["state"] != new_state:
            update_frontend = True
            node["state"] = new_state
            node.save()

    if update_frontend:
        current_app.logger.info("Detected sensor-state change(s), emitting 'change'")
        socketio.emit("change-reading")
        socketio.emit("change")

    return jsonify(message=("Changed" if update_frontend else "Not Changed"))


# Create a user to test with
@bp.before_app_first_request
def create_user():
    current_app.logger.info("Creo utente")
    user_manager.create_user(email="bettarini@monema.it", password="password")


@bp.route("/api-token-test")
@api_token_required
def api_token_test():
    return jsonify({"message": "Valid API Token!"})
