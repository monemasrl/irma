from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from chirpstack_api.as_pb import integration
from google.protobuf.json_format import Parse

import json
from flask import Flask, request, jsonify
from flask_mongoengine import MongoEngine

from datetime import datetime

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

class SentDocument(db.DynamicDocument):
    def to_jsonSent(self):
        return {"data":[
            {
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
                ]
            }
        ]
        }

@app.route('/', methods=['GET'])
def home():
    payload = Payload.objects().order_by('-id').first()#restituisce l'ultimo payload nel database come oggetto di tipo Payload
    #aggiungere creazione di un json che restituisce gli stati, l'ID e i dati degli stacker nel formato fornito da paolo
    id=payload['m2m:cin']['con']['metadata']['sensorId']
    dato=(payload['m2m:cin']['sensorData']['objectJSON'])
    dato=dato.replace("{\"sensorData\":","")
    dato=dato.replace("}","")#ora la stringa contiene solo il valore numerico del campo sensorData
    dato=int(dato)#conversione a dato numerico per confronto con soglie preimpostate
    #print(dato)
    if(dato<15):
        state="ok"
    else:
        state="alert"
    
    collect=Payload.objects().order_by('-id')
    sum=0
    sumM=0
    count=0
    countM=0
    totAverage=0
    monthlyAverage=0
    currentMonth = datetime.now().month
    while payload['m2m:cin']['con']['metadata']['sensorId']=='5': #da modificare perche' scorra tutti gli id
        for x in collect:
            app=x['m2m:cin']['sensorData']['objectJSON']
            app=app.replace("{\"sensorData\":","")
            app=app.replace("}","")
            app=int(app)

            appM=x['m2m:cin']['con']['metadata']['readingTimestamp']
            appM=appM[5:7]
            appM=int(appM)
            if(appM==currentMonth):
                sumM=sumM+app
                countM=countM+1

            sum=sum+app
            count=count+1

        totAverage=sum/count
        monthlyAverage=sumM/countM

    toSend = SentDocument(code=id,status=state,titolo1="Media Letture Totali",dato1=totAverage,titolo2="Media Letture Mensili",dato2=monthlyAverage,titolo3="app",dato3="app")
    return jsonify(toSend.to_jsonSent())


@app.route('/', methods=['POST'])
def create_record():
    record = json.loads(request.data)
    payload = Payload(iD=record['applicationID'],
                time=record['publishedAt'],
                latitude=record['rxInfo'][0]['location']['latitude'],
                longitude=record['rxInfo'][0]['location']['longitude'],
                sensorData=record
                )
    data = payload.from_json(json.dumps(payload.to_json()))
    data.save()
    return jsonify(payload.to_json())


if __name__ == "__main__":
    app.run(debug = True)
