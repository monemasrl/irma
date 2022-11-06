from fastapi import APIRouter, Depends

from ...services.database import User
from ...services.jwt import get_user_from_jwt
from ...utils.alert import alert_info, handle_alert
from .models import HandlePayload

alert_router = APIRouter(prefix="/alert")


@alert_router.post("/handle")
async def handle_alert_route(
    payload: HandlePayload, user: User = Depends(get_user_from_jwt)
):
    from ....app import socketio

    await handle_alert(payload, user)

    socketio.emit("change")
    socketio.emit("change-reading")

    return {"message": "Handled"}


@alert_router.get("/info")
def alert_info_route(alertID: str):
    response = alert_info(alertID)

    return response
