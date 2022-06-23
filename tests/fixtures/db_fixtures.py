"""
Data fixtures of db objects
"""

import pytest
from fixtures.data_fixtures import *
from mockHttp.microservice_websocket import Payload, SentDocument


@pytest.fixture()
def payload(iD, time, latitude, longitude, sensorData):
    return Payload(
        iD=iD,
        time=time,
        latitude=latitude,
        longitude=longitude,
        sensorData=sensorData,
    )