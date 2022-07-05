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


@pytest.fixture()
def sentDocument(decoded_devEUI, sensorId, state) -> SentDocument:
    return SentDocument(
        eui=decoded_devEUI,
        code=sensorId,
        state=state,
        titolo1="Foo",
        titolo2="Bar",
        titolo3="Baz",
        dato1=0.0,
        dato2=0.0,
        dato3=0,
    )
