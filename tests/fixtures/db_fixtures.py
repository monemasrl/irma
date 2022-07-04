"""
Data fixtures of db objects
"""

import pytest
from fixtures.data_fixtures import *
from mockHttp.microservice_websocket import Payload, SentDocument


@pytest.fixture()
def payload(sensorId, readingTimestamp,
            latitude, longitude, sensorData_noUplink) -> Payload:
    return Payload(
        sensorId=sensorId,
        readingTimestamp=readingTimestamp,
        latitude=latitude,
        longitude=longitude,
        sensorData=sensorData_noUplink,
    )
