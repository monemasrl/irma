from flask import Blueprint, current_app, jsonify

from ... import socketio
from ...services.database import Node, user_manager
from ...utils.node import update_state
from .alert import alert_bp
from .application import application_bp
from .external_archiviation import ext_arch_bp
from .jwt import jwt_bp
from .node import node_bp
from .organization import organization_bp
from .payload import payload_bp
from .session import session_bp
from .user import user_bp

bp = Blueprint("api", __name__, url_prefix="/api")

bp.register_blueprint(organization_bp)
bp.register_blueprint(application_bp)
bp.register_blueprint(node_bp)
bp.register_blueprint(payload_bp)
bp.register_blueprint(alert_bp)
bp.register_blueprint(jwt_bp)
bp.register_blueprint(session_bp)
bp.register_blueprint(user_bp)
bp.register_blueprint(ext_arch_bp)


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
    user_manager.create_user(
        email="bettarini@monema.it", password="password", role="admin"
    )
