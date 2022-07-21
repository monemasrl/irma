# Node

## Schema di collegamento

```mermaid
flowchart LR
  node[Node]
  sensori[Sensori]
  msw[microservice_websocket]

  sensori <-- CAN --> node
  node -- POST --> msw
  msw -- MQTT --> node
```

## Lo script

Questo script si occupa di gestire la lettura dei sensori e gestire lo stato di registrazione.

### Schema di comportamento

```mermaid
flowchart TD
  A[\Start/] --> B[Caricamento configurazione]
  B --> C[Inizializzazione CAN e MQTT]
  C --> D[Invio KEEP_ALIVE]
  D --> E[/Attendo pubblicazione sul topic /&ltAPPLICATION_ID&gt/&ltSENSOR_ID&gt/commands/]
  E --> L{Ho ricevuto<br />START_REC?}
  L -- SI --> F[Invio inizio registrazione]
  L -- NO --> E
  F --> G[Leggo dati]
  G --> H[Invio dati]
  H --> I[Invio fine registrazione]
  I --> E

```

### Avviare lo script

Dopo aver inizializzato l'interfaccia CAN (fare riferimento al [readme principale](../README.md)), basta eseguire `app.py` con l'interprete di python:

    python3 app.py

### Configurare lo script

È possibile configurare lo script mediante il file [config.yaml](./config.yaml).

