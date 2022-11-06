# @bp.route("/check")
# def _check_for_updates():
#     nodes = Node.objects()
#
#     update_frontend = False
#
#     for node in nodes:
#         new_state = update_state(node["state"], node["lastSeenAt"])
#
#         if node["state"] != new_state:
#             update_frontend = True
#             node["state"] = new_state
#             node.save()
#
#     if update_frontend:
#         current_app.logger.info("Detected sensor-state change(s), emitting 'change'")
#         socketio.emit("change-reading")
#         socketio.emit("change")
#
#     return jsonify(message=("Changed" if update_frontend else "Not Changed"))

from fastapi import APIRouter

from .alert import alert_router
from .application import application_router
from .external_archiviation import ext_arch_router
from .jwt import jwt_router
from .node import node_router
from .organization import organization_router
from .payload import payload_routr
from .session import session_router
from .user import user_router

main_router = APIRouter(prefix="/api")

main_router.include_router(alert_router)
main_router.include_router(application_router)
main_router.include_router(ext_arch_router)
main_router.include_router(jwt_router)
main_router.include_router(node_router)
main_router.include_router(organization_router)
main_router.include_router(payload_routr)
main_router.include_router(session_router)
main_router.include_router(user_router)
