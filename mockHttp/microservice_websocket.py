from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from google.protobuf.json_format import Parse

import json
from flask import Flask, request, jsonify, Response
from flask_cors import CORS, cross_origin
from flask_socketio import send,emit, SocketIO

from datetime import datetime

import base64

from mockHttp.microservice_db import Payload, SentDocument, init_db

rec=""
MAX_TRESHOLD = 20   # valore teorico della soglia di pericolo del sensore
N_DEVICES = 18      # valore teorico del quantitativo di dispositivi separati per cui cercare gli id nel database


def mSum(data,readTime,currentMonth):
    if(readTime==currentMonth):                                                                                             
        return data
    return 0


def prepare_status(dato):                         
    if(dato==0):
        state="off"
    elif(dato<MAX_TRESHOLD):
        state="ok"
    else:
        state="alert"
    return state


def prepareData(rawData):
    data = json.loads(rawData)['sensorData']
    data=int(data)
    return data


def prepare_month(readTime):
    readTime=readTime[5:7]
    readTime=int(readTime)  
    return readTime

def getData(n,rec):
    totSum=0
    monthlySum=0
    count=0
    mCount=0
    status="off"
    currentMonth = datetime.now().month #salvataggio del valore attuale del mese per il confronto
    totAverage=0
    monthlyAverage=0
    #questa query prende dal database solo i campi sensorId,ReadinTimestamp e objectJSON da tutti i documenti ordinati prima per sensorId e poi readingTimestamp
    collect=Payload.objects().order_by('m2m:cin.con.metadata.sensorId','-m2m:cin.con.metadata.readingTimestamp').only('m2m:cin.con.metadata.sensorId','m2m:cin.con.metadata.readingTimestamp','m2m:cin.sensorData.objectJSON','m2m:cin.sensorData.devEUI')
    for x in collect:
        appID=x['m2m:cin']['con']['metadata']['sensorId']
        if(appID==n):
            appData=x['m2m:cin']['sensorData']['objectJSON']
            appData=prepareData(appData)
            appReadTime=x['m2m:cin']['con']['metadata']['readingTimestamp']
            appReadTime=prepare_month(appReadTime)
            if(rec==appID):
                status="rec"
            else:
                status=prepare_status(appData)
            totSum=totSum+appData
            count=count+1
            checkMonth=mSum(appData,appReadTime,currentMonth)
            if(checkMonth!=0):
                mCount=mCount+1
                monthlySum=monthlySum+checkMonth
            totAverage=totSum/count
            if(mCount!=0):
                monthlyAverage=monthlySum/mCount
    if(status=="ok" or status=="rec"):
        eui=x['m2m:cin']['sensorData']['devEUI']
    else:
        eui=0
    send=json.dumps(SentDocument(eui=eui,code=n,status=status,titolo1="Media Letture Totali",dato1=float("{0:.3f}".format(totAverage)),titolo2="Media Letture Mensili",dato2=float("{0:.3f}".format(monthlyAverage)),titolo3="Letture eseguite nel mese",dato3=mCount).to_jsonSent())
    count=0
    mCount=0
    totSum=0
    monthlySum=0
    return send


def create_socketio(app):
    socketio = SocketIO(app,cors_allowed_origins="*")

    @socketio.on('connect')
    def connected():
        print('Connected')

    @socketio.on('disconnect')
    def disconnected():
        print('Disconnected')

    @socketio.on('change')
    def onChange():
        print('Changed')
        n=0
        send='{\"data\":['
        while(n<N_DEVICES):                                                              
            n=n+1
            n=str(n)
            appSend=getData(n)
            send=send+appSend+","
            n=int(n)
        send = f"{send[0: -1]}"
        send=send+"]}"
        send=jsonify(json.loads(send))
        socketio.send(send)

    return socketio


def create_app():
    app = Flask(__name__)
    socketio = create_socketio(app)

    app.config['SECRET_KEY'] = 'secret!'

    ###########################################################################################
    #####configurazione dei dati relativi al cors per la connessione da una pagina esterna#####
    ###########################################################################################
    app.config['CORS_SETTINGS']= {
        'Content-Type':'application/json',
        'Access-Control-Allow-Origin': 'http://localhost:3000',
        'Access-Control-Allow-Credentials': 'true'
    }
    #########################################################################
    #####configurazione dei dati relativi al database per la connessione#####
    #########################################################################
    app.config['MONGODB_SETTINGS'] = {
        'db': 'irma',
        'host': 'localhost',
        'port': 27017
    }

    @app.route('/', methods=['GET'])
    @cross_origin()
    def home():
        n=0
        send='{\"data\":['
        while(n<18):                                                              #valore teorico del quantitativo di dispositivi separati per cui cercare gli id nel database
            n=n+1
            n=str(n)
            appSend=getData(n)
            send=send+appSend+","
            n=int(n)
        send = f"{send[0: -1]}"
        send=send+"]}"
        send=jsonify(json.loads(send))
        #socketio.send(send)
        return send

    @app.route('/', methods=['POST'])
    def create_record():
        global rec
        record = json.loads(request.data)
        if "confirmedUplink" in record:                                            #filtraggio degli eventi mandati dall'application server in modo da non inserire nel database valori irrilevanti
            record['devEUI']=base64.b64decode(record['devEUI']).hex()
            payload = Payload(iD=record['applicationID'],
                        time=record['publishedAt'],
                        latitude=record['rxInfo'][0]['location']['latitude'],
                        longitude=record['rxInfo'][0]['location']['longitude'],
                        sensorData=record
                        )
            data = payload.from_json(json.dumps(payload.to_json()))
            data.save()
            if rec==record['applicationID']:
                rec=""
            socketio.emit('change')
            print("1")
            return jsonify(payload.to_json())
        else:
            print("Received message different than Uplink")
            rec=record['applicationID']
            socketio.emit('change')
            print("2")
            return {}

    return app, socketio


if __name__ == "__main__":
    app, socketio = create_app()
    db = init_db(app)
    socketio.run(app, debug=True)
