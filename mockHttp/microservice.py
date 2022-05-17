from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from chirpstack_api.as_pb import integration
from google.protobuf.json_format import Parse

import json
from flask import Flask, request, jsonify
from flask_mongoengine import MongoEngine

app = Flask(__name__)

app.config['MONGODB_SETTINGS'] = {
    'db': 'irma',
    'host': 'localhost',
    'port': 27017
}
db = MongoEngine()
db.init_app(app)

#definizione della struttura del documento inserito in mongo
class Payload(db.DynamicDocument):  
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

@app.route('/', methods=['GET'])
def home():
    payload = Payload.objects().order_by('-id').first()#restituisce l'ultimo payload nel database come oggetto di tipo Payload
    return jsonify(payload)


@app.route('/', methods=['POST'])
def create_record():
    record = json.loads(request.data)
    payload = Payload(iD=record['applicationID'],
                time=record['publishedAt'],
                latitude=record['rxInfo'][0]['location']['latitude'],
                longitude=record['rxInfo'][0]['location']['longitude'],
                sensorData=record)
    print(record['objectJSON'])
    data = payload.from_json(json.dumps(payload.to_json()))
    data.save()
    return jsonify(payload.to_json())


if __name__ == "__main__":
    app.run(debug = True)
