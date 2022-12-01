import requests

from ..services.database import Reading
from .exceptions import NotFoundException

SET_NAME = "ext-archiviation-endpoints"


def get_external_endpoints() -> list[str]:
    from .. import redis_client

    endpoints = redis_client.smembers(SET_NAME)

    return [x.decode() for x in endpoints]


def add_external_endpoint(endpoint: str):
    from .. import redis_client

    redis_client.sadd(SET_NAME, endpoint)


def delete_external_endpoint(endpoint: str):
    from .. import redis_client

    if redis_client.srem(SET_NAME, endpoint) == 0:
        raise NotFoundException(endpoint)


async def send_payload(payload: Reading):
    for endpoint in get_external_endpoints():
        serialized_payload = await payload.serialize()
        requests.post(endpoint, json=serialized_payload.dict())
