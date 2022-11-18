from fastapi import APIRouter, Depends

from ...services.database import Alert, User
from ...services.jwt import get_user_from_jwt
from ...utils.alert import get_alert, handle_alert
from .models import HandlePayload

alert_router = APIRouter(prefix="/alert")


@alert_router.post("/{alertID}")
async def handle_alert_route(
    alertID: str, payload: HandlePayload, user: User = Depends(get_user_from_jwt)
):
    from ....app import socketio

    await handle_alert(alertID, payload, user)

    socketio.emit("change")
    socketio.emit("change-reading")

    return {"message": "Handled"}


@alert_router.get("/{alertID}", response_model=Alert.Serialized)
async def get_alert_route(alertID: str):
    response: Alert = await get_alert(alertID)

    return await response.serialize()
