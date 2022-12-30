from beanie import init_beanie
from mongomock_motor import AsyncMongoMockClient
from motor.motor_asyncio import AsyncIOMotorClient

from .models import Alert, Application, NodeSettings, Organization, Reading, User
from ...entities.node import Node


async def init_db(db_uri: str, db_name: str):
    if "mongomock" in db_uri:
        client = AsyncMongoMockClient()
    else:
        client = AsyncIOMotorClient(db_uri)
    db = client[db_name]

    await init_beanie(
        database=db,
        document_models=[
            Organization,
            Application,
            User,
            Node,
            NodeSettings,
            Reading,
            Alert,
        ],
    )
