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


class Payload(db.Document):
    iD = db.StringField()
    time = db.StringField()
    sensorData = db.DynamicField()
    def to_json(self):
        return {"m2m:cin":{
                    "con":{
                        "metadata": {
                            "sensorId": self.iD,
                            "readingTimestamp": self.time,
                            "latitude": 0,
                            "longitude": 0,
                            "heading": 0
                            },
                        "sensorData": self.sensorData
                        }
                    }
                }

@app.route('/', methods=['GET'])
def home():
    return "<h1>Microservice</h1><p>This site is a prototype microservice for IRMA.</p>"


@app.route('/', methods=['POST'])
def create_record():
    
    record = json.loads(request.data)
    payload = Payload(iD=record['applicationID'],
                time=record['publishedAt'],
                sensorData=record)
    print(record['objectJSON'])
    payload.save()
    return jsonify(payload.to_json())

if __name__ == "__main__":
    app.run(debug = True)
