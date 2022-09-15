from ..services.database import Node, Reading
from .exceptions import ObjectNotFoundException


def get_session(nodeID: int, sessionID: int) -> list[Reading]:
    if sessionID == -1:
        latest_reading = Reading.object(nodeID=nodeID).order_by("-sessionID").first()
        if latest_reading is None:
            raise ObjectNotFoundException(Reading)

        sessionID = latest_reading["sessionID"]

    readings = Reading.objects(nodeID=nodeID, sessionID=sessionID)

    return [x.to_dashboard() for x in readings]


def get_sessions_id(nodeID: int) -> list[int]:
    node = Node.objects(nodeID=nodeID).first()

    if node is None:
        raise ObjectNotFoundException(Node)

    sessions = Reading.objects(nodeID=nodeID).only("sessionID")

    sessions_id = [x["sessionID"] for x in sessions]

    # Remove duplicates
    sessions_id = list(set(sessions_id))

    return sessions_id
