from beanie.operators import And, Eq

from ..services.database import Node, Reading
from .exceptions import NotFoundException


async def get_session(nodeID: int, sessionID: int | None) -> list[Reading]:
    node: Node | None = await Node.find_one(Node.nodeID == nodeID)
    if node is None:
        raise NotFoundException("Node")

    if sessionID is None:
        latest_reading: Reading | None = await (
            Reading.find(Reading.node == node.id).sort("-sessionID").first_or_none()
        )
        if latest_reading is None:
            return []

        sessionID = latest_reading.sessionID

    readings: list[Reading] = await Reading.find(
        And(
            Eq(Reading.node, node.id),
            Eq(Reading.sessionID, sessionID),
        )
    ).to_list()

    return [x for x in readings]


async def get_sessions_id(nodeID: int) -> list[int]:
    node: Node | None = await Node.find_one(Node.nodeID == nodeID)
    if node is None:
        raise NotFoundException("Node")

    sessions: list[Reading] = await Reading.find(Reading.node == node.id).to_list()

    sessions_id = [x.sessionID for x in sessions]

    # Remove duplicates
    sessions_id = list(set(sessions_id))

    return sessions_id
