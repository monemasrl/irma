from __future__ import annotations

from flask import Flask
from flask_mongoengine import Document, MongoEngine
from mongoengine import IntField
from mongoengine.fields import (
    BooleanField,
    DateTimeField,
    ListField,
    ReferenceField,
    StringField,
)

from ...utils.enums import NodeState


def init_db(app: Flask):
    database = MongoEngine()
    database.init_app(app)


###############################################################
# definizione della struttura del documento inserito in mongo #
###############################################################
class Organization(Document):
    organizationName = StringField(max_length=100, required=True)


class Application(Document):
    applicationName = StringField(max_length=100, required=True)
    organization = ReferenceField(Organization)


class Role(Document):
    name = StringField(max_length=80, unique=True)
    description = StringField(max_length=255)


class User(Document):
    email = StringField(max_length=255)
    password = StringField(max_length=255)  # User information
    first_name = StringField(default="")
    last_name = StringField(default="")
    roles = ListField(ReferenceField(Role), default=[])


class Node(Document):
    nodeID = IntField(required=True)
    nodeName = StringField(default="", required=True)
    application = ReferenceField(Application, required=True)
    organization = ReferenceField(Organization, required=True)
    state = IntField(required=True)
    lastSeenAt = DateTimeField(required=True)

    def to_dashboard(self) -> dict:
        unhandledAlerts = Alert.objects(node=self, isHandled=False)

        unhandledAlertIDs = [str(x["id"]) for x in unhandledAlerts]

        return {
            "nodeID": self.nodeID,
            "nodeName": self.nodeName,
            "applicationID": str(self.application["id"]),
            "state": NodeState.to_irma_ui_state(self.state),
            "unhandledAlertIDs": unhandledAlertIDs,
        }


class Reading(Document):
    nodeID = IntField(required=True)
    canID = IntField(required=True)
    sensorNumber = IntField(required=True)
    readingID = IntField(default=0)
    sessionID = IntField(required=True)
    dangerLevel = IntField(required=True)
    window1_count = IntField(required=True)
    window2_count = IntField(required=True)
    window3_count = IntField(required=True)
    publishedAt = DateTimeField(required=True)

    def to_dashboard(self) -> dict:
        return {
            "canID": self.canID,
            "sensorNumber": self.sensorNumber,
            "readingID": self.readingID,
            "sessionID": self.sessionID,
            "dangerLevel": self.dangerLevel,
            "window1_count": self.window1_count,
            "window2_count": self.window2_count,
            "window3_count": self.window3_count,
            "publishedAt": str(self.publishedAt),
        }


class Alert(Document):
    reading = ReferenceField(Reading, required=True)
    node = ReferenceField(Node, required=True)
    sessionID = IntField(required=True)
    isHandled = BooleanField(required=True)
    isConfirmed = BooleanField()
    handledBy = ReferenceField(User)
    handledAt = DateTimeField()
    handleNote = StringField()
