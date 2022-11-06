from datetime import datetime
from typing import Optional

from beanie import Document, Link
from pydantic import Field

from ...utils.enums import NodeState


class Organization(Document):
    organizationName: str


class Application(Document):
    applicationName: str
    organization: Link[Organization]


class User(Document):
    email: str
    hashed_password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str = "standard"


class Node(Document):
    nodeID: int
    nodeName: str
    application: Link[Application]
    state: NodeState
    lastSeenAt: datetime


class Reading(Document):
    node: Link[Node]
    canID: int = Field(default=..., lt=5, gt=0)
    sensorNumber: int = Field(default=..., lt=3, gt=0)
    readingID: int
    sessionID: int
    dangerLevel: int = 0
    window1: int = 0
    window2: int = 0
    window3: int = 0
    publishedAt: datetime


class Alert(Document):
    reading: Link[Reading]
    node: Link[Node]
    sessionID: int
    isHandled: bool = False
    raisedAt: datetime
    isConfirmed: bool = False
    handledBy: Optional[Link[User]] = None
    handledAt: Optional[datetime] = None
    handleNote: str = ""
