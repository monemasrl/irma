from pydantic import BaseModel

from ...utils.enums import PayloadType


class HandlePayload(BaseModel):
    alertID: str
    isConfirmed: bool
    handleNote: str


class PublishPayloadData(BaseModel):
    value: int
    count: int
    sessionID: int
    readingID: int
    canID: int
    sensorNumber: int


class PublishPayload(BaseModel):
    applicationID: str
    nodeID: int
    nodeName: str
    payloadType: PayloadType
    data: PublishPayloadData | None
