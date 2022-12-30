from typing import Literal

from pydantic import BaseModel


class ReadingPayloadData(BaseModel):
    value: int
    count: int
    sessionID: int
    readingID: int
    canID: int
    sensorNumber: int


class ReadingPayload(BaseModel):
    payloadType: Literal["total", "window"]
    data: ReadingPayloadData
