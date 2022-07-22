from __future__ import annotations
from flask_mongoengine import Document
from mongoengine import IntField
from mongoengine.fields import StringField, \
    ReferenceField, ListField, BooleanField, \
    DateTimeField, EmbeddedDocumentListField, EmbeddedDocument
from flask_security import Security, MongoEngineUserDatastore, \
    UserMixin, RoleMixin, login_required
import json




#####################################################################
#####definizione della struttura del documento inserito in mongo#####
#####################################################################
class Organization(Document):
    organizationName=StringField(max_length=100, required=True)

class Application(Document):
    applicationName=StringField(max_length=100, required=True)
    organization=ReferenceField(Organization)

class Role(Document, RoleMixin):
    name = StringField(max_length=80, unique=True)
    description = StringField(max_length=255)

class User(Document, UserMixin):
    email = StringField(max_length=255)
    password = StringField(max_length=255)    # User information
    fs_uniquifier = StringField(max_length=64, unique=True)
    first_name = StringField(default='')
    last_name = StringField(default='')
    active = BooleanField(default=True)
    confirmed_at = DateTimeField()
    roles = ListField(ReferenceField(Role), default=[])

class Sensor(Document):
    sensorID = IntField(required=True)
    application = ReferenceField(Application, required=True)
    organization = ReferenceField(Organization, required=True)
    sensorName = StringField(default='', required=True)
    state = IntField(required=True)

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
    isConfirmed = BooleanField(required=True)
    confirmedBy = ReferenceField(User)
    confirmTime = DateTimeField()
    confirmNote = StringField()