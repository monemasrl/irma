# class Node(Document):
#     def to_dashboard(self) -> dict:
#         unhandledAlerts = Alert.objects(node=self, isHandled=False)
#
#         unhandledAlertIDs = [str(x["id"]) for x in unhandledAlerts]
#
#         return {
#             "nodeID": self.nodeID,
#             "nodeName": self.nodeName,
#             "applicationID": str(self.application["id"]),
#             "state": NodeState.to_irma_ui_state(self.state),
#             "unhandledAlertIDs": unhandledAlertIDs,
#         }


from beanie import init_beanie
from mongomock_motor import AsyncMongoMockClient
from motor.motor_asyncio import AsyncIOMotorClient

from .models import Alert, Application, Node, Organization, Reading, User


async def init_db(db_uri: str, db_name: str):
    if "mongomock" in db_uri:
        client = AsyncMongoMockClient()
    else:
        client = AsyncIOMotorClient(db_uri)
    db = client[db_name]

    await init_beanie(
        database=db,
        document_models=[Organization, Application, User, Node, Reading, Alert],
    )
