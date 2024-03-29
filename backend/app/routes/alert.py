from fastapi import APIRouter, Depends

from ..controllers.alert import get_alert, handle_alert
from ..services.database import Alert, User
from ..services.jwt import get_user_from_jwt
from .models import HandlePayload

alert_router = APIRouter(prefix="/alert")


@alert_router.post("/{alertID}", tags=["alert"])
async def handle_alert_route(
    alertID: str, payload: HandlePayload, user: User = Depends(get_user_from_jwt)
):
    from .. import socketManager

    await handle_alert(alertID, payload, user)

    socketManager.emit("change-node")

    return {"message": "Handled"}


@alert_router.get("/{alertID}", response_model=Alert.Serialized, tags=["alert"])
async def get_alert_route(alertID: str):
    response: Alert = await get_alert(alertID)

    return await response.serialize()
