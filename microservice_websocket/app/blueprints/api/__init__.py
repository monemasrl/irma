from fastapi import APIRouter

from .alert import alert_router
from .application import application_router
from .command import command_router
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
main_router.include_router(command_router)
main_router.include_router(ext_arch_router)
main_router.include_router(jwt_router)
main_router.include_router(node_router)
main_router.include_router(organization_router)
main_router.include_router(payload_routr)
main_router.include_router(session_router)
main_router.include_router(user_router)
