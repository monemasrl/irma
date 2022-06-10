# PROGETTO IRMA

#### DESCRIZIONE PROGETTO

Rete di comunicazione a lunga gittata tramite protocollo LoRa per la trasmissione di dati raccolti da sensori verso il server che raccoglie e elabora i dati ritrasmettendoli tramite un web-service a una dashboard.


#### APPLICATION SERVER

Il setup dell' application server in locale su Ubuntu contiene pochi passi essenziali:

##### 1-Creazione di un database e uno user in postgres:

    sudo -u postgres psql
    create role chirpstack_as with login password 'dbpassword';

    create database chirpstack_as with owner chirpstack_as;

    \c chirpstack_as
    create extension pg_trgm;
    create extension hstore;

    \q
    
##### 2-Download della repository precompilata:

    sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 1CE2AFD36DBCCA00

    sudo echo "deb https://artifacts.chirpstack.io/packages/3.x/deb stable main" | sudo tee /etc/apt/sources.list.d/chirpstack.list
    sudo apt-get update
    
##### 3-Installazione dell'application server

    sudo apt-get install chirpstack-application-server


#### NETWORK SERVER

Il setup del network server in locale su Ubuntu contiene pochi passi essenziali:

##### 1-Creazione di un database e uno user in postgres:

    sudo -u postgres psql
    create role chirpstack_ns with login password 'dbpassword';

    create database chirpstack_ns with owner chirpstack_ns;

    \q
    
##### 2-Download della repository precompilata:

    sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 1CE2AFD36DBCCA00

    sudo echo "deb https://artifacts.chirpstack.io/packages/3.x/deb stable main" | sudo tee /etc/apt/sources.list.d/chirpstack.list
    sudo apt update
    
##### 3-Installazione dell'application server

    sudo apt install chirpstack-network-server


#### GATEWAY

<img src="assets\raspi4.jpeg" width="150" height="150"/>

Per la connessione del gateway è stato utilizzato un **HAT RAK2245** e un **Raspberry Pi 4B+** con relativa repository per l'installazione del service:
  
    $ sudo apt update; sudo apt install git -y
  
    $ git clone https://github.com/RAKWireless/rak_common_for_gateway.git ~/rak_common_for_gateway
  
    $ cd ~/rak_common_for_gateway
  
    $ sudo ./install.sh

Dopo queste operazioni si può eseguire il comando `sudo gateway-config` per configurare la connessione del proprio gateway al server.


#### END-DEVICE

Per connettere un nuovo end-device su lorawan è necessario sapere il Device EUI che viene fornito dalla scheda che si usa e bisogna fare il join tramite una delle due modalità **(OTAA o ABP)**.

Il device va registrato sul server tramite l'interfaccia web Applications > [Nome applicazione_da_utilizzare] > Create

Sull'end device nel file [serial_esp_lora_oled.ino](arduino-py-communication/serial_esp_lora_oled.ino) vanno inseriti i dati relativi alle chiavi della rete che si trovano all'interno del menu del device creato in precedenza sul server.

Per la lettura dei dati va scritto un decoder su misura per i dati che verranno ricevuti sul device profile selezionato per la crezione del device sull'application server. 

### ***ATTENZIONE!!!***
*Il file **.ino** fornito nella repository è stato testato solo su un **Heltec ESP32** e non è garantito il funzionamento su altri dispositivi non basati su ESP32*

<img src="assets\esp.png" width="100" height="100"/>

Per aggiungere la lettura dei dati dai sensori è stato utilizzato il protocollo CAN con l'aggiunta di un **Raspberry Pi 2B** in modo da ricevere i dati sulla interfaccia seriale 

<img src="assets\raspi2.png" width="120" height="120"/>

#### WEB-SERVICE E SALVATAGGIO DEI DATI

Il server chirpstack non mantiene i dati trasmessi dagli end-device in nessun modo permanente, perciò sull'application server è stata attivata da interfaccia web l'integrazione con HTTP la quale permette di eseguire un POST con l'intero payload in formato JSON. Il file [microservice.py](mockHttp/microservice.py) si occupa della ricezione del POST e l'inserimento dei JSON in un database Mongo, dopo di che i dati dal database vengono rielaborati e ritrasmessi sempre in formato JSON alla dashboard tramite una richiesta GET per il display dei valori. 

#### COMANDI

Il file [downlink.py](downlink.py) si occupa dell'invio dei comandi di Start e Stop all'application server tramite MQTT, il quale a sua volta invierà un messaggio di downlink verso l'end-device con il comando ricevuto il quale fermerà o avvierà la lettura dei dati dai sensori. Questo script serve per il test dei comandi senza dashboard.

Per l'utilizzo degli stessi comandi ma da dashboard in remoto si usa il file [downlink_microservice.py](mockHttp/downlink_microservice.py) che riceve un post dalla dashboard con un valore numerico che definisce il messaggio da inviare tramite MQTT(Start o Stop) e lo pubblica sul topic dell'application server.


#### TESTING IN LOCALE

Al fine di eseguire dei test in locale per mancanza di una rete LoRaWAN da utilizzare sono stati utilizzati due script:

1. [auto_can.py](auto_can.py) - 
    Questo script eseguito (solo per test) sul gateway invia tramite interfaccia CAN due messaggi a intervalli regolari.
    
2. [arduino_communication.py](arduino-py-communication/arduino_communication.py) - 
    Questo script eseguito su un Rapberry Pi connesso all'ESP32 riceve tramite interfaccia CAN i messaggi che successivamente ritrasmetterà attraverso intefaccia seriale all'end-device.


Questo sistema sotituisce la necessità di una rete e di sensori funzionanti per fare test sul funzionameto della infrastruttura di rete.
