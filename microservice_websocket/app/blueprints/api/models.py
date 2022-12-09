from pydantic import BaseModel

from ...utils.enums import PayloadType


class HandlePayload(BaseModel):
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


class CreateUserPayload(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    role: str


class UpdateUserPayload(BaseModel):
    email: str | None = None
    first_name: str | None
    last_name: str | None
    old_password: str | None = None
    new_password: str | None = None
    role: str | None = None
