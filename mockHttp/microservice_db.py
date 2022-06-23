from flask_mongoengine import MongoEngine, DynamicDocument
from flask import Flask


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