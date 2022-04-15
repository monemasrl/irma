# PROGETTO IRMA

#### DESCRIZIONE PROGETTO

Rete di comunicazione a lunga gittata tramite protocollo LoRa per la trasmissione di dati raccolti da sensori verso il server che raccoglie e elabora i dati ritrasmettendoli tramite un web-service a una dashboard.

#### END-DEVICE

Per connettere un nuovo end-device su lorawan è necessario sapere il Device EUI che viene fornito dalla scheda che si usa e bisogna fare il join tramite una delle due modalità **(OTAA o ABP)**.

Il device va registrato sul server tramite l'interfaccia web Applications > [Nome applicazione_da_utilizzare] > Create

Sull'end device nel file **.ino** vanno inseriti i dati relativi alle chiavi della rete che si trovano all'interno del menu del device creato in precedenza sul server.

Per la lettura dei dati va scritto un decoder sul device profile selezionato per la crezione del device sul server. 

### ***ATTENZIONE!!!***
*Il file **.ino** fornito nella repository è stato testato solo su un **Heltec ESP32** e non funzionerà su altri dispositivi non basati su ESP32*

#### GATEWAY

Per la connessione del gateway è stato utilizzato un **HAT RAK2245** e un **Raspberry Pi 3B+** con relativa repository per l'installazione del service:
  
    $ sudo apt update; sudo apt install git -y
  
    $ git clone https://github.com/RAKWireless/rak_common_for_gateway.git ~/rak_common_for_gateway
  
    $ cd ~/rak_common_for_gateway
  
    $ sudo ./install.sh

Dopo queste operazioni si può eseguire il comando `sudo gateway-config` per configurare la connessione del proprio gateway al server.

#### WEB-SERVICE

Sull'application server è stata attivata da interfaccia l'integrazione con HTTP la quale permette di eseguire un POST con l'intero payload in formato JSON. Il file [microservice.py](mockHttp/microservice.py) si occupa della ricezione del POST e l'inserimento dei json in un database mongo, dopo di che i dati dal database vengono presi e reinviati a un altro host dopo una richesta GET.
