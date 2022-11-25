from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ...services.jwt import jwt_required
from ...utils.command import send_mqtt_command
from ...utils.enums import CommandType

command_router = APIRouter(prefix="/command")


class MqttCommandPayload(BaseModel):
    nodeID: int
    applicationID: str


@command_router.post("/{command_type}", dependencies=[Depends(jwt_required)])
async def send_mqtt_command_route(
    command_type: CommandType, payload: MqttCommandPayload
):
    await send_mqtt_command(payload.applicationID, payload.nodeID, command_type)

    return {"message": "Sent"}
