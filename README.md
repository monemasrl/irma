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

Sull'end device nel file **.ino** vanno inseriti i dati relativi alle chiavi della rete che si trovano all'interno del menu del device creato in precedenza sul server.

Per la lettura dei dati va scritto un decoder su misura per i dati che verranno ricevuti sul device profile selezionato per la crezione del device sull'application server. 

### ***ATTENZIONE!!!***
*Il file **.ino** fornito nella repository è stato testato solo su un **Heltec ESP32** e non funzionerà su altri dispositivi non basati su ESP32*

<img src="assets\esp.png" width="100" height="100"/>

Per aggiungere la lettura dei dati dai sensori è stato utilizzato il protocollo CAN con l'aggiunta di un **Raspberry Pi 2B** in modo da ricevere i dati sulla interfaccia seriale 

<img src="assets\raspi2.png" width="100" height="100"/>

#### WEB-SERVICE

Sull'application server è stata attivata da interfaccia l'integrazione con HTTP la quale permette di eseguire un POST con l'intero payload in formato JSON. Il file [microservice.py](mockHttp/microservice.py) si occupa della ricezione del POST e l'inserimento dei json in un database mongo, dopo di che i dati dal database vengono presi e reinviati a un altro host dopo una richesta GET.

#### COMANDI

Il file [downlink.py](downlink.py) si occupa dell'invio dei comandi di Start e Stop all'application server tramite MQTT, il quale a sua volta invierà un messaggio di downlink verso l'end-device con il comando ricevuto il quale fermerà o avvierà la lettura dei dati dai sensori.
