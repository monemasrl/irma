from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..controllers.command import handle_command
from ..services.jwt import jwt_required
from ..utils.enums import CommandType

command_router = APIRouter(prefix="/command")


class MqttCommandPayload(BaseModel):
    nodeID: int
    applicationID: str


@command_router.post(
    "/{command_type}", dependencies=[Depends(jwt_required)], tags=["command"]
)
async def send_mqtt_command_route(
    command_type: CommandType, payload: MqttCommandPayload
):
    await handle_command(command_type, payload.applicationID, payload.nodeID)

    return {"message": "Sent"}
