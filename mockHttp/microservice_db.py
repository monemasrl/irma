from __future__ import annotations
from flask_mongoengine import MongoEngine, Document
from mongoengine.fields import DictField, StringField, FloatField, IntField
from flask import Flask
import json


def init_db(app: Flask) -> MongoEngine:
    db = MongoEngine()
    db.init_app(app)
    return db


#####################################################################
#####definizione della struttura del documento inserito in mongo#####
#####################################################################
class Payload(Document):
    sensorId = StringField(max_length=100, required=True)
    readingTimestamp = StringField(max_length=100, required=True)
    latitude = FloatField(required=True)
    longitude = FloatField(required=True)
    sensorData = DictField(required=True)

    def to_json(self) -> dict:
        return {
            "m2m:cin": {
                "con": {
                    "metadata": {
                        "sensorId": self.sensorId,
                        "readingTimestamp": self.readingTimestamp,
                        "latitude": self.latitude,
                        "longitude": self.longitude,
                    },
                },
                "sensorData":self.sensorData,
            }
        }

    @classmethod
    def from_json(cls, s: str) -> Payload:
        s_dict = json.loads(s)
        new_p = Payload()
        new_p.sensorId = s_dict["m2m:cin"]["con"]["metadata"]["sensorId"]
        new_p.readingTimestamp = s_dict["m2m:cin"]["con"]["metadata"]["readingTimestamp"]
        new_p.latitude = s_dict["m2m:cin"]["con"]["metadata"]["latitude"]
        new_p.longitude = s_dict["m2m:cin"]["con"]["metadata"]["longitude"]
        new_p.sensorData = s_dict["m2m:cin"]["sensorData"]

        return new_p
        

#############################################################################
#####definizione struttura del documento da reinviare alla richiesta GET#####
#############################################################################
class SentDocument(Document):
    eui = StringField(max_length=100, required=True)
    status = StringField(max_length=100, required=True)
    code = StringField(max_length=100, required=True)
    titolo1 = StringField(max_length=100, required=True)
    titolo2 = StringField(max_length=100, required=True)
    titolo3 = StringField(max_length=100, required=True)
    dato1 = FloatField(required=True)
    dato2 = FloatField(required=True)
    dato3 = IntField(required=True)

    def to_json(self) -> dict:
        return {
            "devEUI":self.eui,
            "state": self.status,
            "code": self.code,
            "datiInterni": [
                {
                    "titolo": self.titolo1,
                    "dato": self.dato1
                },
                {
                    "titolo": self.titolo2,
                    "dato": self.dato2
                },
                {
                    "titolo": self.titolo3,
                    "dato": self.dato3
                },
            ],
        }
