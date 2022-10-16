from datetime import datetime, timedelta

from ..config import config
from ..services.database import Reading
from .external_archiviation import send_payload


def add_to_cache(readingObjectID: str):
    from .. import redis_client

    redis_client.sadd("idCache", readingObjectID)


def sync_cached():
    from .. import redis_client

    ids: list[str] = redis_client.smembers("idCache")

    # Loop set items
    for readingObjectId in [x.decode() for x in ids]:
        reading: Reading = Reading.objects(id=readingObjectId).first()
        if reading is None:
            redis_client.srem("idCache", readingObjectId)

        publishedAt = reading["publishedAt"]

        if datetime.now() - publishedAt > timedelta(
            seconds=config["READING_SYNC_WAIT"]
        ):
            send_payload(reading.serialize())
            redis_client.srem("idCache", readingObjectId)
