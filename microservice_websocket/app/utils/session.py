from beanie.operators import And, Eq

from ..services.database import Node, Reading
from .exceptions import NotFoundException


async def get_session(nodeID: int, sessionID: int | None) -> list[Reading.Aggregated]:
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
                            "sensorNumber": "$sensor_number",
                        },
                        "merged": {
                            "$push": {
                                "canID": "$canID",
                                "sensorNumber": "$sensor_number",
                                "readingID": "$readingID",
                                "window1": "$window1",
                                "window2": "$window2",
                                "window3": "$window3",
                                "dangerLevel": "$danger_level",
                            }
                        },
                    }
                },
                {"$replaceRoot": {"newRoot": {"$mergeObjects": "$merged"}}},
                {"$addFields": {"nodeID": node.nodeID, "sessionID": sessionID}},
            ],
            projection_model=Reading.Aggregated,
        )
        .to_list()
    )

    return readings


async def get_sessions_id(nodeID: int) -> list[int]:
    node: Node | None = await Node.find_one(Node.nodeID == nodeID)
    if node is None:
        raise NotFoundException("Node")

    sessions_id: list[int] = await Reading.distinct("sessionID", {"node": node.id})

    return sessions_id
