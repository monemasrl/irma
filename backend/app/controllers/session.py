from beanie.operators import And, Eq

from ..exceptions import NotFoundException
from ..services.database import Node, Reading


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
                            "sensor_number": "$sensor_number",
                        },
                        "data": {"$addToSet": {"name": "$name", "value": "$value"}},
                        "published_at": {"$max": "$published_at"},
                    }
                },
                {
                    "$project": {
                        "data": {
                            "$arrayToObject": {
                                "$zip": {"inputs": ["$data.name", "$data.value"]}
                            }
                        },
                        "published_at": 1,
                    }
                },
                {
                    "$replaceRoot": {
                        "newRoot": {
                            "readingID": "$_id.readingID",
                            "canID": "$_id.canID",
                            "sensorNumber": "$_id.sensor_number",
                            "window1": "$data.w1",
                            "window2": "$data.w2",
                            "window3": "$data.w3",
                            "dangerLevel": "$data.t",
                            "publishedAt": {"$toLong": "$published_at"},
                        }
                    }
                },
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
