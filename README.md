
mock script for the communication between two Raspberry pi devices trough can bus and script for the communication between a Raspberry pi and an ESP32 trough serial port of the data collected by the can bus

END-DEVICE

Per connettere un nuovo end-device su lorawan è necessario sapere il Device EUI che viene fornito dalla scheda che si usa e bisogna fare il join tramite una delle due modalità (OTAA o ABP).

Il device va registrato sul server tramite l'interfaccia web Applications > [Nome applicazione_da_utilizzare] > Create

Sull'end device nel file .ino vanno inseriti i dati relativi alle chiavi della rete che si trovano all'interno del menu del device creato in precedenza sul server.

Per la lettura dei dati va scritto un decoder sul device profile selezionato per la crezione del device sul server. 

GATEWAY

Per la connessione del gateway è stato utilizzato un HAT RAK2245 con relativa repository per l'installazione del service:
  
  $ sudo apt update; sudo apt install git -y
  
  $ git clone https://github.com/RAKWireless/rak_common_for_gateway.git ~/rak_common_for_gateway
  
  $ cd ~/rak_common_for_gateway
  
  $ sudo ./install.sh

Dopo queste operazioni si può eseguire il comando gateway-config per configurare la connessione del proprio gateway al server.

