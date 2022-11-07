from __future__ import annotations

from datetime import datetime

from beanie import Document, PydanticObjectId
from beanie.exceptions import DocumentWasNotSaved
from pydantic import Field

from ...utils.enums import NodeState


class CustomDocument(Document):
    @property
    def id(self) -> PydanticObjectId:
        obj_id = super().id
        if obj_id is None:
            raise DocumentWasNotSaved

        return obj_id


class Organization(CustomDocument):
    organizationName: str


class Application(CustomDocument):
    applicationName: str
    organization: PydanticObjectId


class User(CustomDocument):
    email: str
    hashed_password: str
    first_name: str = ""
    last_name: str = ""
    role: str = "standard"


class Node(CustomDocument):
    nodeID: int
    nodeName: str
    application: PydanticObjectId
    state: NodeState
    lastSeenAt: datetime


class Reading(CustomDocument):
    node: PydanticObjectId
    canID: int = Field(default=..., lt=5, gt=0)
    sensorNumber: int = Field(default=..., lt=3, gt=0)
    readingID: int
    sessionID: int
    dangerLevel: int = 0
    window1: int = 0
    window2: int = 0
    window3: int = 0
    publishedAt: datetime


class Alert(CustomDocument):
    reading: PydanticObjectId
    node: PydanticObjectId
    sessionID: int
    isHandled: bool = False
    raisedAt: datetime
    isConfirmed: bool = False
    handledBy: PydanticObjectId | None = None
    handledAt: datetime | None = None
    handleNote: str = ""
