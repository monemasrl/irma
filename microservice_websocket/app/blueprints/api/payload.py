from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel

from ...services.jwt import jwt_required
from ...utils.api_token import verify_api_token
from ...utils.payload import publish, send_mqtt_command
from .models import PublishPayload

payload_routr = APIRouter(prefix="/payload")


class MqttCommandPayload(BaseModel):
    nodeID: str
    applicationID: str
    command: int


@payload_routr.post("/publish")
async def publish_route(
    payload: PublishPayload, authorization: str | None = Header(default=None)
):
    verify_api_token(authorization)

    await publish(payload)

    from ... import socketio

    socketio.emit("change")
    socketio.emit("change-reading")
    return {"message": "Published"}


@payload_routr.post("/command", dependencies=[Depends(jwt_required)])
async def send_mqtt_command_route(payload: MqttCommandPayload):
    await send_mqtt_command(payload.applicationID, payload.nodeID, payload.command)

    return {"message": "Sent"}
