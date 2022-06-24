from __future__ import annotations
from flask_mongoengine import MongoEngine, DynamicDocument
from flask import Flask
import json


def init_db(app: Flask) -> MongoEngine:
    db = MongoEngine()
    db.init_app(app)
    return db

#####################################################################
#####definizione della struttura del documento inserito in mongo#####
#####################################################################
class Payload(DynamicDocument):  
    def to_json(self):
        return {"m2m:cin":{
                    "con":{
                        "metadata": {
                            "sensorId": self.iD,
                            "readingTimestamp": self.time,
                            "latitude": self.latitude,
                            "longitude": self.longitude
                            }
                        },
                    "sensorData":self.sensorData
                    }
                }

    @classmethod
    def from_json(self, s: str) -> Payload:
        s_dict = json.loads(s)
        new_p = Payload()
        new_p.iD = s_dict["m2m:cin"]["con"]["metadata"]["sensorId"]
        new_p.time = s_dict["m2m:cin"]["con"]["metadata"]["readingTimestamp"]
        new_p.latitude = s_dict["m2m:cin"]["con"]["metadata"]["latitude"]
        new_p.longitude = s_dict["m2m:cin"]["con"]["metadata"]["longitude"]
        new_p.sensorData = s_dict["m2m:cin"]["sensorData"]

        return new_p
#############################################################################
#####definizione struttura del documento da reinviare alla richiesta GET#####
#############################################################################
class SentDocument(DynamicDocument):
    def to_jsonSent(self):
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
                    }
                ]
        }