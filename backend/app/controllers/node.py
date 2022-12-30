from beanie import PydanticObjectId

from ..entities.node import Node
from ..exceptions import NotFoundException
from ..services.database import Application


async def get_nodes(applicationID: str):
    application: Application | None = await Application.get(
        PydanticObjectId(applicationID)
    )
    if application is None:
        raise NotFoundException("Application")

    nodes: list[Node] = await Node.find(Node.application == application.id).to_list()

    return nodes
