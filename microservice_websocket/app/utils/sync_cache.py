from datetime import datetime, timedelta

from ..services.database import Reading
from ..services.mobius import utils as mobius_utils

# TODO: move to config file
SYNC_TIME = timedelta(minutes=1)


def add_to_cache(readingObjectID: str):
    from .. import redis_client

    redis_client.sadd("idCache", readingObjectID)


def sync_cached():
    from .. import redis_client

    ids: list[str] = redis_client.smembers("idCache")

    # Loop set items
    for readingObjectId in [x.decode() for x in ids]:
        reading = Reading.objects(id=readingObjectId).first()
        if reading is None:
            redis_client.srem("idCache", readingObjectId)

        publishedAt = reading["publishedAt"]

        if datetime.now() - publishedAt > SYNC_TIME:
            mobius_utils.insert(reading)
            redis_client.srem("idCache", readingObjectId)
