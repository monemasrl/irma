# PROGETTO IRMA ![testing on branch master](https://github.com/monemasrl/irma/actions/workflows/irma-ci.yml/badge.svg?branch=master)

## DESCRIZIONE PROGETTO

Rete di comunicazione a lunga gittata tramite protocollo LoRa per la trasmissione di dati raccolti da sensori verso il server che raccoglie e elabora i dati ritrasmettendoli tramite un web-service a una dashboard.

### Struttura progetto
```mermaid
graph TD;

chirpstack[chirpstack-docker]
msw[microservice_websocket.py]
mm[mock_mobius]
db[MongoDB]
dms[downlink_microservice.py]
irma-ui[Irma UI]

gateway[Gateway LoRaWAN]
nodo[Nodo]
sensori[Sensori]

chirpstack -- POST / 5000 --> msw
msw -- POST / 5002 --> mm
msw -- GET / 5002 --> mm
mm <--> db
irma-ui <-- HTTP 5000 e websocket --> msw
irma-ui -- POST / 5001 --> dms
dms -- MQTT 1883 --> chirpstack
gateway -- UDP 1700 --> chirpstack
nodo -- LoRa --> gateway
sensori -- CAN --> nodo
```

## CHIRPSTACK DEPLOYMENT

All'interno della directory [chirpstack-docker](chirpstack-docker) è presente il file [docker-compose.yaml](chirpstack-docker/docker-compose.yaml), grazie al quale è possibile dispiegare l'intero stack di servizi di chirpstack. All'interno della cartella sono presenti anche i file di configurazione dei vari servizi lanciati da docker.

Per utilizzare [docker-compose.yaml](chirpstack-docker/docker-compose.yaml):

    docker-compose up -d
    
Per visualizzare i logs:

    docker-compose logs -f

Per fermare i container (e smontare i volumi):

    docker-compose down (-v)
    
Il [Chirpstack Application Server](https://www.chirpstack.io/application-server/) è raggiungibile mediante la porta 8080 sull'host. Le credenziali predefinite per accedere alla dashboard sono username: `admin` e password: `admin`.

### Encode e decode del payload

All'interno della cartella [chirpstack-docker](chirpstack-docker) è presente il file [encode_decode.js](chirpstack-docker/encode_decode.js) che contiene il codice da integrare nella sezione ** dell'interfaccia web dell'Application Server.

### Struttura interna [docker-compose.yaml](chirpstack-docker/docker-compose.yaml)

```mermaid
graph TD;
subgraph chirpstack-docker;
  direction LR;
    redis[redis]
    cgb[chirpstack-gateway-bridge]
    cns[chirpstack-network-server]
    cas[chirpstack-application-server]
    mqtt[eclipse-mosquitto]
    db[(PostgreSQL)]

    cas -- HTTP 8000 --> cns
    cgb & cns <-- TCP 1883 --> mqtt
    cas & cns <-- TCP 6379 --> redis
    cns & cas <--> db
end
out([host network])
mqtt <-- TCP 1883 --> out
cas -- HTTP 8080 --> out
cgb -- UDP 1700 --> out
```

## GATEWAY

<img src="assets\raspi4.jpeg" width="150" height="150"/>

Per la connessione del gateway è stato utilizzato un **HAT RAK2245** e un **Raspberry Pi 4B+** con relativa repository per l'installazione del service:
  
    $ sudo apt update; sudo apt install git -y
  
    $ git clone https://github.com/RAKWireless/rak_common_for_gateway.git ~/rak_common_for_gateway
  
    $ cd ~/rak_common_for_gateway
  
    $ sudo ./install.sh

Dopo queste operazioni si può eseguire il comando `sudo gateway-config` per configurare la connessione del proprio gateway al server.


## END-DEVICE

Per connettere un nuovo end-device su lorawan è necessario sapere il Device EUI che viene fornito dalla scheda che si usa e bisogna fare il join tramite una delle due modalità **(OTAA o ABP)**.

Bisogna creare una applicazione sul server tramite interfaccia web Applications > Create.

Successivamente va registrato il device Applications > [Nome applicazione_da_utilizzare] > Create.
Bisogna inserire il device EUI durante la registrazione, esso viene fornito dal produttore nella sua documentazione.

Sull'end device nel file [serial_esp_lora_oled.ino](arduino-py-communication/serial_esp_lora_oled.ino) vanno inseriti i dati relativi alle chiavi della rete che si trovano all'interno del menu del device creato in precedenza sul server.

Per la lettura dei dati va scritto un decoder su misura per i dati che verranno ricevuti sul device profile selezionato per la crezione del device sull'application server. 

> :warning: **Warning**: *Il file **.ino** fornito nella repository è stato testato solo su un **Heltec ESP32** e non è garantito il funzionamento su altri dispositivi non basati su ESP32* :warning:

<img src="assets\esp.png" width="100" height="100"/>

Per aggiungere la lettura dei dati dai sensori è stato utilizzato il protocollo CAN con l'aggiunta di un **Raspberry Pi 2B** in modo da ricevere i dati sulla interfaccia seriale 

<img src="assets\raspi2.png" width="120" height="120"/>

### Struttura nodo/end-device

```mermaid
graph LR;
Sensori <-- CAN --> Nodo -- LoRa --> Gateway
```

## WEB-SERVICE E SALVATAGGIO DEI DATI

Il server chirpstack non mantiene i dati trasmessi dagli end-device in nessun modo permanente, perciò sull'application server da interfaccia web deve essere attivata l'integrazione con HTTP, che permette di eseguire una POST con l'intero payload in formato JSON. 

Il modulo [microservice_websocket](microservice_websocket/) si occupa della ricezione del POST e l'inoltro dei JSON al servizio [mock_mobius](mock_mobius/) che simula il comportamento della piattaforma Mobius (piattaforma per la registrazione dei dati).

Inoltre, [microservice_websocket](microservice_websocket/) si occupa anche di gestire la connession alla dashboard mediante WebSocket e di effettuare le query a [mock_mobius](mock_mobius/)

### Avvio di [microservice_websocket](microservice_websocket/)

Per scaricare le **dipendenze** è possibile eseguire:

    pip3 install -r requirements.txt

Poi per avviare il servizio:

    python3 -m mockHttp.microservice_websocket

### Avviare [mock_mobius](mock_mobius/)

Per le **dipendenze** far riferimento al paragrafo precedente.

[mock_mobius](mock_mobius/) richiede un'istanza [MongoDB](https://www.mongodb.com/) su localhost.

Per avviare il servizio:

    FLASK_APP=mock_mobius flask run --port=5002

## COMANDI

Il file [downlink.py](downlink.py) si occupa dell'invio dei comandi di Start e Stop all'application server tramite MQTT, il quale a sua volta invierà un messaggio di downlink verso l'end-device con il comando ricevuto il quale fermerà o avvierà la lettura dei dati dai sensori. Questo script serve per il test dei comandi senza dashboard.

Per l'utilizzo degli stessi comandi ma da dashboard in remoto si usa il file [downlink_microservice.py](mockHttp/downlink_microservice.py) che riceve un post dalla dashboard con un valore numerico che definisce il messaggio da inviare tramite MQTT(Start o Stop) e due valori che rappresentano gli id dell'applicazione e del dispositivo che servono per pubblicare sul topic dell'application server.


## TESTING IN LOCALE

Al fine di eseguire dei test in locale per mancanza di una rete LoRaWAN da utilizzare sono stati utilizzati due script:

1. [auto_can.py](auto_can.py) - 
    Questo script eseguito (solo per test) sul gateway invia tramite interfaccia CAN due messaggi a intervalli regolari.
    
2. [arduino_communication.py](arduino-py-communication/arduino_communication.py) - 
    Questo script eseguito su un Rapberry Pi connesso all'ESP32 riceve tramite interfaccia CAN i messaggi che successivamente ritrasmetterà attraverso intefaccia seriale all'end-device.


Questo sistema sotituisce la necessità di una rete e di sensori funzionanti per fare test sul funzionameto della infrastruttura di rete.

### Struttura testing locale

```mermaid
graph LR;
rpi4[Raspberry PI 4 - gateway]
subgraph nodo
  rpi2[Raspberry PI 2]
  esp[ESP32]
end

rpi2 -- Serial --> esp
esp -- LoRa --> rpi4
rpi4 -- CAN --> rpi2
rpi4 -- UDP 1700 --> chirpstack
```

### Inizializzazione interfaccia CAN

Per utilizzare l'interfaccia CAN è talvolta necessario inizializzarla prima di eseguire gli script sopra-citati.

Le istruzioni da eseguire sono:

    $ sudo modprobe peak_usb
    $ sudo ip link set can0 up type can bitrate 500000
    
Per maggiori info consultare la documentazione di [python-can](https://python-can.readthedocs.io/en/stable/interfaces/socketcan.html#pcan).
