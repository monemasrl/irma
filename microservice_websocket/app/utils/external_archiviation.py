import requests

from .exceptions import ObjectNotFoundException

SET_NAME = "ext-archiviation-endpoints"


def get_external_endpoints() -> list[str]:
    from .. import redis_client

    endpoints = redis_client.smembers(SET_NAME)

    if len(endpoints) == 0:
        raise ObjectNotFoundException(str)

    return [x.decode() for x in endpoints]


def add_external_endpoint(endpoint: str):
    from .. import redis_client

    redis_client.sadd(SET_NAME, endpoint)


def delete_external_endpoint(endpoint: str):
    from .. import redis_client

    if redis_client.srem(SET_NAME, endpoint) == 0:
        raise ObjectNotFoundException(str)


def send_payload(payload: dict):
    try:
        for endpoint in get_external_endpoints():
            requests.post(endpoint, json=payload)
    except ObjectNotFoundException:
        pass
