# Node

## Schema di collegamento

Il nodo comunica con i rilevatori tramite [interfaccia CAN](https://it.wikipedia.org/wiki/Controller_Area_Network).

### Inizializzazione interfaccia CAN

Per utilizzare l'interfaccia CAN è talvolta **necessario inizializzarla**.

Le istruzioni da eseguire sono:

    $ sudo modprobe peak_usb
    $ sudo ip link set can0 up type can bitrate 500000

Per maggiori informazioni consultare la documentazione di [python-can](https://python-can.readthedocs.io/en/stable/interfaces/socketcan.html#pcan).

#### Inizializzazione al boot

Per poter inizializare l'interfaccia al boot del dispositivo, e' stato inserito uno script  all'interno di [pi-configs](./pi-configs/).

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
h --> M[Richiesta TOTAL COUNT\nai sensori]
f -- NO --> g{E' SET_DEMO_1?}
g -- SI --> N[Lancio request task\ncon demo1]
g -- NO --> O{E' SET_DEMO_2?}
O -- SI --> R[Lancio request task\ncon demo2]
O -- NO --> Q[Error]
e --> i
M --> i
N --> i
R --> i

b -- NO --> i{E' disponbile un<br />messagio sul CAN BUS?}
i -- NO --> b
i -- SI --> j[Decodifico il messagio]
j --> k[Invio il messaggio al backend]
k --> b

subgraph KEEP_ALIVE daemon
  L[\Inizio/] --> D[Invio ON_LAUNCH]
  D --> E[Sleep]
  E --> F[Invio KEEP_ALIVE]
  F --> E
end

subgraph request task
  G[\Inzio/] --> H[Richiesta WINDOW COUNT\nai sensori]
  H --> P[Sleep]
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
