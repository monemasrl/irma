from __future__ import annotations
from flask_mongoengine import Document
from mongoengine.fields import DictField, StringField, FloatField
import json




#####################################################################
#####definizione della struttura del documento inserito in mongo#####
#####################################################################
class Payload(Document):
    id=StringField(max_length=100, required=True)
    sensorPath = StringField(max_length=100, required=True)
    sensorId = StringField(max_length=100, required=True)
    readingTimestamp = StringField(max_length=100, required=True)
    latitude = FloatField(required=True)
    longitude = FloatField(required=True)
    sensorData = DictField(required=True)

    def to_json(self) -> dict:
        return {
            "pi": "",
            "ri": self.id,
            "ct": self.readingTimestamp, # ?
            "con": {
                "metadata": {
                    "sensorId": self.sensorId,
                    "readingTimestamp": self.readingTimestamp,
                    "latitude": self.latitude,
                    "longitude": self.longitude,
                },
            },
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
