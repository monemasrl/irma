from __future__ import annotations

from flask_mongoengine import Document
from mongoengine import IntField
from mongoengine.fields import (
    BooleanField,
    DateTimeField,
    EmbeddedDocument,
    EmbeddedDocumentListField,
    ListField,
    ReferenceField,
    StringField,
)


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


class Sensor(Document):
    sensorID = IntField(required=True)
    application = ReferenceField(Application, required=True)
    organization = ReferenceField(Organization, required=True)
    sensorName = StringField(default="", required=True)
    state = IntField(required=True)
    lastSeenAt = DateTimeField(required=True)


class Data(EmbeddedDocument):
    payloadType = IntField(required=True)
    sensorData = IntField(required=True)
    publishedAt = DateTimeField(required=True)
    mobius_sensorId = StringField(required=True)
    mobius_sensorPath = StringField(required=True)


class Reading(Document):
    sensor = ReferenceField(Sensor, required=True)
    requestedAt = DateTimeField(required=True)
    data = EmbeddedDocumentListField(Data, required=True)


class Alert(Document):
    reading = ReferenceField(Reading, required=True)
    sensor = ReferenceField(Sensor, required=True)
    isHandled = BooleanField(required=True)
    isConfirmed = BooleanField()
    handledBy = ReferenceField(User)
    handledAt = DateTimeField()
    handleNote = StringField()
