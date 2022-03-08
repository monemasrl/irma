
mock script for the communication between two Raspberry pi devices trough can bus and script for the communication between a Raspberry pi and an ESP32 trough serial port of the data collected by the can bus

Per connettere un nuovo end-device su lorawan è necessario sapere il Device EUI che viene fornito dalla scheda che si usa e bisogna fare il join tramite una delle due modalità (OTAA o ABP).

Il device va registrato sul server tramite l'interfaccia web Applications > [Nome applicazione_da_utilizzare] > Create

Sull'end device vanno inseriti i dati relativi alle chiavi della rete che si trovano all'interno del menu del device creato in precedenza sul server.

Per la lettura dei dati va scritto un decoder sul device profile selezionato per la crezione del device sul server. 
