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
    metadata = db.StringField()
    sensorData = db.StringField()
    def to_json(self):
        return {"metadata": self.metadata,
                "sensorData": self.sensorData}

@app.route('/', methods=['GET'])
def home():
    return "<h1>Microservice</h1><p>This site is a prototype microservice for IRMA.</p>"


@app.route('/', methods=['POST'])
def update_record():
    
    record = json.loads(request.data)
    payload = Payload(metadata=record['applicationID'],
                sensorData=record['applicationID'])
    print(record['objectJSON'])
    payload.save()
    return jsonify(payload.to_json())

if __name__ == "__main__":
    app.run(debug = True)
