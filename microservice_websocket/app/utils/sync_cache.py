from datetime import datetime, timedelta

from beanie import PydanticObjectId

from ..config import config as Config
from ..services.database import Reading
from .external_archiviation import send_payload


def add_to_cache(readingObjectID: str):
    from .. import redis_client

    redis_client.sadd("idCache", readingObjectID)


async def sync_cached():
    from .. import redis_client

    ids: set[bytes] = redis_client.smembers("idCache")

    # Loop set items
    for reading_object_id in [x.decode() for x in ids]:
        reading: Reading | None = await Reading.get(PydanticObjectId(reading_object_id))
        if reading is None:
            redis_client.srem("idCache", reading_object_id)
            continue

        publishedAt = reading.publishedAt

        if datetime.now() - publishedAt > timedelta(
            seconds=Config.app.READING_SYNC_WAIT
        ):
            await send_payload(reading)
            redis_client.srem("idCache", reading_object_id)
