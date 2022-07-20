from __future__ import annotations
from flask_mongoengine import Document, ReferenceField, ListField, BooleanField, DateTimeField
from mongoengine.fields import DictField, StringField, FloatField
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
    first_name = StringField(default='')
    last_name = StringField(default='')
    active = BooleanField(default=True)
    confirmed_at = DateTimeField()
    roles = ListField(ReferenceField(Role), default=[])