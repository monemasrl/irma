import json
from flask import Flask, request
from flask_mqtt import Mqtt

from flask_cors import CORS


def create_mqtt(app: Flask) -> Mqtt:
    mqtt = Mqtt(app)

    @mqtt.on_connect() # connessione al topic mqtt
    def handle_connect(client, userdata, flags, rc):
        mqtt.subscribe('application')

    @mqtt.on_message() # preparazione del messaggio da pubblicare sul topic
    def handle_mqtt_message(client, userdata, message):
        data = dict(
            topic=message.topic,
            payload=message.payload.decode()
        )
    
    return mqtt


def create_app():
    app: Flask = Flask(__name__)

    ###########################################################################################
    #####configurazione dei dati relativi al cors per la connessione da una pagina esterna#####
    ###########################################################################################
    app.config['CORS_SETTINGS']= {
        'Content-Type':'application/json',
        'Access-Control-Allow-Origin': 'http://localhost:3000',
        'Access-Control-Allow-Credentials': 'true'
    }

    ################################################################
    #####configurazione dei dati relativi alla connessione MQTT#####
    ################################################################
    app.config['MQTT_BROKER_URL'] = 'localhost'
    app.config['MQTT_BROKER_PORT'] = 1883
    app.config['MQTT_TLS_ENABLED'] = False

    CORS(app)

    mqtt: Mqtt = create_mqtt(app)

    @app.route('/', methods=['GET'])
    def home():
        return """
            <html>
                <head>
                    <title>downlink_microservice</title>
                </head>
                <body>
                    <div>Script di invio messaggi MQTT per l'avvio dei comandi Start e Stop degli end-device</div>
                </body>
            </html>
        """

    @app.route('/', methods=['POST'])
    def sendMqtt(): # alla ricezione di un post pubblica un messaggio sul topic
        received: dict = json.loads(request.data)

        # application ID ricevuto per identificare le varie app sull'application server
        appNum: str = str(received['app']['code'])
        # devEUI rivuto per identificare i dipositivi nelle varie app
        devEUI: str = str(received['app']['devEUI'])
        topic: str = 'application/'+appNum+'/device/'+devEUI+'/command/down'

        start: str = 'U3RhcnQ='
        stop: str = 'U3RvcA=='

        data: str = json.dumps({
            'confirmed': False,
            'fPort': 2,
            'data': start if received['statoStaker'] == 1 else stop
        })

        mqtt.publish(topic, data.encode())
        print(received)
        return received
    
    return app


if __name__ == "__main__":
    create_app().run(port=5001, debug=True)
