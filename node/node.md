# Node

## Schema di collegamento

Il nodo comunica con i rilevatori tramite [interfaccia CAN](https://it.wikipedia.org/wiki/Controller_Area_Network).

### Inizializzazione interfaccia CAN

Per utilizzare l'interfaccia CAN è talvolta **necessario inizializzarla**.

Le istruzioni da eseguire sono:

    $ sudo modprobe peak_usb
    $ sudo ip link set can0 up type can bitrate 500000

Per maggiori informazioni consultare la documentazione di [python-can](https://python-can.readthedocs.io/en/stable/interfaces/socketcan.html#pcan).

## Lo script

Questo script si occupa di gestire i **rilevatori**.

### Schema di comportamento

```mermaid
flowchart TD;
A[\Start/] --> B[Caricamento configurazione]
B --> C[Inizializzazione CAN e MQTT]
C --> a[Lancio KEEP_ALIVE daemon]
a --> b{E' disponbile un messaggio<br />sul topic mqtt?}
b -- SI --> c[Decodifica il messaggio]
c --> d{E' START_REC?}
d -- SI --> e[Lancio requst task]
d -- NO --> f{E' END_REC?}
f -- SI --> h[Fermo request task]
f -- NO --> g[ERRORE]
e --> i
h --> i

b -- NO --> i{E' disponbile un<br />messagio sul CAN BUS?}
i -- NO --> b
i -- SI --> j[Decodifico il messagio]
j --> k[Invio il messaggio<br />a microservice_websocket]
k --> b

subgraph KEEP_ALIVE daemon
  D[Invio END_REC] --> E[Sleep]
  E --> F[Invio KEEP_ALIVE]
  F --> E
end

subgraph request task
  G[Inzio] --> H[Richiesta TOTAL COUNT a S1]
  H --> I[Richiesta TOTAL COUNT a S2]
  I --> J[Richiesta WINDOW COUNT 1 a S1]
  J --> K[Richiesta WINDOW COUNT 1 a S2]
  K --> L[Richiesta WINDOW COUNT 2 a S1]
  L --> M[Richiesta WINDOW COUNT 2 a S2]
  M --> N[Richiesta WINDOW COUNT 3 a S1]
  N --> O[Richiesta WINDOW COUNT 3 a S2]
  O --> P[Sleep]
  P --> H
end
```

### Avviare lo script

Dopo aver [inizializzato l'interfaccia CAN](./node.md#inizializzazione-interfaccia-can), basta eseguire `app.py` con l'interprete di python:

    python3 app.py

### Configurare lo script

È possibile configurare lo script mediante il file [config.yaml](./config.yaml).

### Modalità di testing

Per effettuare il **testing**, è possibile avviare lo script settando la **variabile d'ambiente** `BYPASS_CAN`.
