from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..controllers.node import get_nodes
from ..entities.node import Node
from ..services.database import NodeSettings
from ..services.jwt import jwt_required
from ..utils.node_settings import get_node_settings, update_node_settings

node_router = APIRouter()


class GetNodesResponse(BaseModel):
    nodes: list[Node.Serialized]


@node_router.get(
    "/nodes/", dependencies=[Depends(jwt_required)], response_model=GetNodesResponse
)
async def get_nodes_route(applicationID: str):
    nodes: list[Node] = await get_nodes(applicationID)

    return {"nodes": [await x.serialize() for x in nodes]}


@node_router.get(
    "/node/{nodeID}/settings",
    dependencies=[Depends(jwt_required)],
    response_model=NodeSettings.Serialized,
)
async def get_node_settings_route(nodeID: int):
    settings: NodeSettings = await get_node_settings(nodeID)

    return settings.serialize()


@node_router.put("/node/{nodeID}/settings", dependencies=[Depends(jwt_required)])
async def update_node_settings_route(payload: NodeSettings.Serialized, nodeID: int):
    from .. import socketManager

    await update_node_settings(nodeID, payload)

    socketManager.emit("settings-update")

    return {"message": "Updated"}
