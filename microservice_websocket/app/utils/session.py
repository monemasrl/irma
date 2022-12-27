from beanie.operators import And, Eq

from ..services.database import Node, Reading
from .exceptions import NotFoundException


async def get_session(nodeID: int, sessionID: int | None) -> list[Reading]:
    node: Node | None = await Node.find_one(Node.nodeID == nodeID)
    if node is None:
        raise NotFoundException("Node")

    if sessionID is None:
        sessions_id = await get_sessions_id(nodeID)
        if len(sessions_id) == 0:
            return []

        sessionID = max(sessions_id)

    readings = (
        await Reading.find(
            And(Eq(Reading.node, node.id), Eq(Reading.sessionID, sessionID))
        )
        .aggregate(
            [
                {
                    "$group": {
                        "_id": {
                            "readingID": "$readingID",
                            "canID": "$canID",
                            "sensor_number": "$sensor_number",
                        },
                        "merged": {
                            "$push": {
                                "canID": "$canID",
                                "sensor_number": "$sensor_number",
                                "readingID": "$readingID",
                                "window1": "$window1",
                                "window2": "$window2",
                                "window3": "$window3",
                                "danger_level": "$danger_level",
                                "published_at": {"$max": "$published_at"},
                            }
                        },
                    }
                },
                {"$replaceRoot": {"newRoot": {"$mergeObjects": "$merged"}}},
                {"$addFields": {"node": node.id, "sessionID": sessionID}},
            ],
            projection_model=Reading,
        )
        .to_list()
    )

    print(readings)

    return readings


async def get_sessions_id(nodeID: int) -> list[int]:
    node: Node | None = await Node.find_one(Node.nodeID == nodeID)
    if node is None:
        raise NotFoundException("Node")

    sessions_id: list[int] = await Reading.distinct("sessionID", {"node": node.id})

    return sessions_id
