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

def mSum(data,readTime,currentMonth):
    if(readTime==currentMonth):                                                                                             
        return data
    return 0

def prepare_status(dato):                           
    if(dato==0):
        state="off"
    elif(dato<15):
        state="ok"
    else:
        state="alert"
    return state

def prepareData(appData):
    appData=appData.replace("{\"sensorData\":","")
    appData=appData.replace("}","")                                                           #ora la stringa contiene solo il valore numerico del campo sensorData
    appData=int(appData)   
    return appData     

def prepare_month(readTime):
    readTime=readTime[5:7]
    readTime=int(readTime)  
    return readTime

def getData(n):
    totSum=0
    monthlySum=0
    count=0
    mCount=0
    status="off"
    currentMonth = datetime.now().month
    totAverage=0
    monthlyAverage=0
    collect=Payload.objects().order_by('m2m:cin.con.metadata.sensorId','-m2m:cin.con.metadata.readingTimestamp').only('m2m:cin.con.metadata.sensorId','m2m:cin.con.metadata.readingTimestamp','m2m:cin.sensorData.objectJSON')
    
    for x in collect:
        appID=x['m2m:cin']['con']['metadata']['sensorId']
        if(appID==n):
            appData=x['m2m:cin']['sensorData']['objectJSON']
            appData=prepareData(appData)
            appReadTime=x['m2m:cin']['con']['metadata']['readingTimestamp']
            appReadTime=prepare_month(appReadTime)
            status=prepare_status(appData)
            totSum=totSum+appData
            count=count+1
            checkMonth=mSum(appData,appReadTime,currentMonth)
            if(checkMonth!=0):
                mCount=mCount+1
                monthlySum=monthlySum+checkMonth
            totAverage=totSum/count
            monthlyAverage=monthlySum/mCount

    send=json.dumps(SentDocument(code=n,status=status,titolo1="Media Letture Totali",dato1=totAverage,titolo2="Media Letture Mensili",dato2=monthlyAverage,titolo3="Letture eseguite nel mese",dato3=totSum).to_jsonSent())
    count=0
    mCount=0
    totSum=0
    monthlySum=0
    return send
    

@app.route('/', methods=['GET'])
def home():    
    n=0
    send=''
    while(n<18):
        n=n+1
        n=str(n)
        appSend=getData(n)
        send=send+appSend
        n=int(n)
    return send


@app.route('/', methods=['POST'])
def create_record():
    record = json.loads(request.data)
    if "confirmedUplink" in record:
        payload = Payload(iD=record['applicationID'],
                    time=record['publishedAt'],
                    latitude=record['rxInfo'][0]['location']['latitude'],
                    longitude=record['rxInfo'][0]['location']['longitude'],
                    sensorData=record
                    )
        data = payload.from_json(json.dumps(payload.to_json()))
        data.save()
        return jsonify(payload.to_json())
    else:
        print("Received message different than Uplink")
        return {}

if __name__ == "__main__":
    app.run(debug = True)
