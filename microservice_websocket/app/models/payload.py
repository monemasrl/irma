from pydantic import BaseModel
from typing import Literal


class ReadingPayloadData(BaseModel):
    value: int
    count: int
    sessionID: int
    readingID: int
    canID: int
    sensorNumber: int


class ReadingPayload(BaseModel):
    applicationID: str
    nodeID: int
    nodeName: str
    payloadType: Literal["total", "window"]
    data: ReadingPayloadData
