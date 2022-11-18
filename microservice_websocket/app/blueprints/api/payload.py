from fastapi import APIRouter, Header

from ...utils.api_token import verify_api_token
from ...utils.payload import publish
from .models import PublishPayload

payload_routr = APIRouter(prefix="/payload")


@payload_routr.post("/")
async def publish_route(
    payload: PublishPayload, authorization: str | None = Header(default=None)
):
    verify_api_token(authorization)

    await publish(payload)

    from ... import socketio

    socketio.emit("change")
    socketio.emit("change-reading")

    return {"message": "Published"}
