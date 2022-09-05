
Il [Chirpstack Application Server](https://www.chirpstack.io/application-server/) è raggiungibile mediante la porta 8080 sull'host. Le credenziali predefinite per accedere alla dashboard sono username: `admin` e password: `admin`.

## GATEWAY LORAWAN

Per la connessione del gateway è stato utilizzato un **HAT RAK2245** e un [**Raspberry Pi 4B+**](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/) con relativa [repository](https://github.com/RAKWireless/rak_common_for_gateway.git) per l'installazione del service:

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

Per la lettura dei dati va scritto un decoder su misura per i dati che verranno ricevuti sul device profile selezionato per la crezione del device sull'application server. Viene fornito un esempio qui: [encode_decode.js](chirpstack-docker/encode_decode.js).

Durante la fase di registrazione è necessario inserire anche i dati relativi alla piattaforma Mobius (sensorId e sensor_path) nella sezione Tags del sensore.

> :warning: **Warning**: *Il file **.ino** fornito nella repository è stato testato solo su un **Heltec ESP32** e non è garantito il funzionamento su altri dispositivi non basati su ESP32* :warning:

Per aggiungere la lettura dei dati dai sensori è stato utilizzato il protocollo CAN con l'aggiunta di un **Raspberry Pi 2B** in modo da ricevere i dati sulla interfaccia seriale
