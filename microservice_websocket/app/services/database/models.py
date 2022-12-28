from __future__ import annotations

from datetime import datetime
from typing import Literal

from app.utils.exceptions import NotFoundException
from beanie import Document, PydanticObjectId
from beanie.exceptions import DocumentWasNotSaved
from beanie.operators import And, Eq
from pydantic import BaseModel, Field

from ...models.node_settings import DetectorSettings
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

    class Serialized(BaseModel):
        id: str
        organizationName: str

    def serialize(self) -> Organization.Serialized:
        return Organization.Serialized(
            id=str(self.id), organizationName=self.organizationName
        )


class Application(CustomDocument):
    applicationName: str
    organization: PydanticObjectId

    class Serialized(BaseModel):
        id: str
        applicationName: str
        organization: str

    def serialize(self) -> Application.Serialized:
        return Application.Serialized(
            id=str(self.id),
            applicationName=self.applicationName,
            organization=str(self.organization),
        )


class User(CustomDocument):
    email: str
    hashed_password: str
    first_name: str
    last_name: str
    role: str = "standard"

    class Serialized(BaseModel):
        id: str
        email: str
        first_name: str
        last_name: str
        role: str

    def serialize(self) -> User.Serialized:
        return User.Serialized(
            id=str(self.id),
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
            role=self.role,
        )


class NodeSettings(CustomDocument):
    node: PydanticObjectId
    d1: DetectorSettings | None = None
    d2: DetectorSettings | None = None
    d3: DetectorSettings | None = None
    d4: DetectorSettings | None = None

    class Serialized(BaseModel):
        d1: DetectorSettings | None
        d2: DetectorSettings | None
        d3: DetectorSettings | None
        d4: DetectorSettings | None

    def serialize(self) -> NodeSettings.Serialized:
        return NodeSettings.Serialized(
            d1=self.d1,
            d2=self.d2,
            d3=self.d3,
            d4=self.d4,
        )


class Node(CustomDocument):
    nodeID: int
    nodeName: str
    application: PydanticObjectId
    state: NodeState
    lastSeenAt: datetime

    class Serialized(BaseModel):
        nodeID: int
        nodeName: str
        application: str
        state: str
        lastSeenAt: int
        unhandledAlertIDs: list[str]

    async def serialize(self) -> Node.Serialized:
        unhandledAlerts = await Alert.find(
            And(Eq(Alert.node, self.id), Eq(Alert.isHandled, False))
        ).to_list()
        unhandledAlertIDs = [str(x.id) for x in unhandledAlerts]

        return Node.Serialized(
            nodeID=self.nodeID,
            nodeName=self.nodeName,
            application=str(self.application),
            state=NodeState.to_irma_ui_state(self.state),
            lastSeenAt=int(self.lastSeenAt.timestamp()),
            unhandledAlertIDs=unhandledAlertIDs,
        )


class Reading(CustomDocument):
    node: PydanticObjectId
    canID: int = Field(default=..., lt=5, gt=0)
    sensor_number: int = Field(default=..., lt=3, gt=0)
    readingID: int
    sessionID: int

    name: Literal["w1", "w2", "w3", "t"]
    value: int = 0
    published_at: datetime

    class Aggregated(BaseModel):
        nodeID: int
        canID: int
        sensorNumber: int
        sessionID: int
        readingID: int
        window1: int = 0
        window2: int = 0
        window3: int = 0
        dangerLevel: int = 0
        publishedAt: int


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

    class Serialized(BaseModel):
        id: str
        nodeID: int
        sessionID: int
        readingID: int
        canID: int
        raisedAt: int

    async def serialize(self) -> Alert.Serialized:
        node = await Node.get(self.node)
        if node is None:
            raise NotFoundException("Node")

        reading = await Reading.get(self.reading)
        if reading is None:
            raise NotFoundException("Reading")

        return Alert.Serialized(
            id=str(self.id),
            nodeID=node.nodeID,
            sessionID=self.sessionID,
            readingID=reading.readingID,
            canID=reading.canID,
            raisedAt=int(self.raisedAt.timestamp()),
        )
