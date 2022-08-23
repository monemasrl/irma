from __future__ import annotations

import json

from flask_mongoengine import Document
from mongoengine.fields import DictField, FloatField, StringField


#####################################################################
#####definizione della struttura del documento inserito in mongo#####
#####################################################################
class Reading(Document):
    readingId = StringField(max_length=100, required=True)
    sensorPath = StringField(max_length=100, required=True)
    sensorId = StringField(max_length=100, required=True)
    readingTimestamp = StringField(max_length=100, required=True)
    latitude = FloatField()
    longitude = FloatField()
    sensorData = DictField(required=True)

    def to_json(self) -> dict:
        return {
            "pi": "",
            "ri": self.readingId,
            "ct": self.readingTimestamp,  # ?
            "con": {
                "metadata": {
                    "sensorId": self.sensorId,
                    "readingTimestamp": self.readingTimestamp,
                    "latitude": self.latitude,
                    "longitude": self.longitude,
                },
            },
            "sensorData": self.sensorData,
        }

    @classmethod
    def from_json(cls, s: str) -> Reading:
        s_dict = json.loads(s)
        print(s_dict)
        new_p = Reading()
        new_p.sensorId = s_dict["m2m:cin"]["con"]["metadata"]["sensorId"]
        new_p.readingTimestamp = s_dict["m2m:cin"]["con"]["metadata"][
            "readingTimestamp"
        ]
        new_p.sensorData = s_dict["m2m:cin"]["sensorData"]

        return new_p
