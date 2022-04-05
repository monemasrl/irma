from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from chirpstack_api.as_pb import integration
from google.protobuf.json_format import Parse

import json
import flask
from flask_mongoengine import MongoEngine

app = flask.Flask(__name__)



app.config['MONGODB_SETTINGS'] = {
    'db': 'irma',
    'host': 'localhost',
    'port': 27017
}
db = MongoEngine()
db.init_app(app)


newPayload={
    "m2m:cin":{
        "con":{

        }
    }
}

@app.route('/', methods=['GET'])
def home():
    return "<h1>Distant Reading Archive</h1><p>This site is a prototype API for distant reading of science fiction novels.</p>"


@app.route('/', methods=['POST'])
def update_record():
    record = json.loads(request.data)
    


if __name__ == "__main__":
    app.run(debug = True)