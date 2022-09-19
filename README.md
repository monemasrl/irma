# PROGETTO IRMA ![testing on branch master](https://github.com/monemasrl/irma/actions/workflows/irma-ci.yml/badge.svg?branch=master)

I risultati dei test al seguente url:

* [https://irma-tests.netlify.app/](https://irma-tests.netlify.app/)

Per visualizzare la copertura del codice:

* [https://irma-tests.netlify.app/coverage](https://irma-tests.netlify.app/coverage)


## Descrizione progetto

Rete di comunicazione per **trasmissione e raccolta** dati dei sensori. Il server che li riceve si occupa poi di elaborarli ed inviarli alla **dashboard web** [irma-ui](https://github.com/monemasrl/irma-ui.git).

### Struttura progetto

```mermaid
flowchart TD;

msw[microservice_websocket]
mm[mock_mobius]
irma-ui[Irma UI]

nodo[Nodo]
rilevatori[Rilevatori]

msw -- POST 5002 --> mm
irma-ui -- HTTP 5000 --> msw
nodo -- HTTP 5000 --> msw
msw -- MQTT** 1883 --> nodo
rilevatori <-- CAN --> nodo
```

> \*\*Per effettuare la comunicazione tramite MQTT è necessario un **Broker MQTT**.

## DEPLOYMENT

All'interno della **root** principale sono è presente il file [docker-compose.yaml](./docker-compose.yaml), grazie al quale è possibile dispiegare l'intero **stack di servizi**.

### Schema docker-compose.yaml


```mermaid
flowchart TD;

subgraph docker
    mqtt[eclipse-mosquitto]
    mobius[mock_mobius]
    mongo[(MongoDB)]
    msw[microservice_websocket]

    msw -- TCP 1883 --> mqtt
    mobius <--> mongo
    msw <--> mongo
    msw -- HTTP 5002 --> mobius
end
out([host network])
out -- TCP 1883 --> mqtt
out -- HTTP 5000 --> msw

```

## I DATI

### Encode e decode dei dati (da aggiornare)

Per agevolare la trasmissione, i dati vengono codificati in **stringhe base64**. Una volta convertita nuovamente in bytes, la struttura è la seguente:

    |payload_type: 1 byte|sensorData: 4 byte|mobius_sensorId: 10 byte|mobius_sensorPath: 10 byte| 

- `payload_type`: numoro **intero** che rappresenta il **tipo di messaggio** che viene inviato. Fare riferimento al capitolo sugli **Enum**.
- `sensorData`: numero **intero**, **big endian** che rappresenta la **lettura** del sensore.
- `mobius_sensorId`: **stringa** di 10 caratteri, padding a **destra**, richiesta per l'inserimento della lettura sulla piattaforma **Mobius**.
- `mobius_sensorPath`: **stringa** di 10 caratteri, padding a **destra**, richiesta per l'inserimento della lettura sulla piattaforma **Mobius**.

Esempio di **payload base64**: `AQAAAAdtb2JpdXNJZCAgbW9iaXVzUGF0aA==`

Lo stesso payload **decodificato**:

```json
{
  "payloadType": 1,
  "sensorData": 7,
  "mobius_sensorId": "mobiusId",
  "mobius_sensorPath": "mobiusPath"
}
```


### Encode e decode dei payload MQTT (da aggiornare)

Come per il paragrafo precedente, la trasmissione avviene con **strighe base64**. Una volta convertita nuovamente in bytes, la struttura è la seguente:

    |command: 1 byte|commandTimestamp: x bytes|

- `command`: numero **intero** che rappresenta il tipo di comando inviato. Fare riferimento al capitolo sugli **Enum**.
- `commandTimestamp`: **stringa** contenente un **timestamp ISO8601**, per raggruppare le letture relative ad un singolo comando di **start recording**.


## GLI ENUM

Per **ridurre** il **numero di dati** trasmessi, ma al contempo **mantenere la leggebilità**, sono stati creati diversi **IntEnum** per identificare diverse proprietà.

### PayloadType

Identifica i messaggi inviati.

| Nome         | Valore |
|--------------|--------|
| READING      |   0    |
| START_REC    |   1    |
| END_REC      |   2    |
| KEEP_ALIVE   |   3    |
| HANDLE_ALERT |   4    |


### CommandType

| Nome       | Valore |
|------------|--------|
| START_REC  |    0   |
| END_REC    |    1   |

### SensorState

Rappresenta lo stato che può essere assunto dai vari sensori.

| Nome          | Valore |
|---------------|--------|
| ERROR         |   0    |
| READY         |   1    |
| RUNNING       |   2    |
| ALERT_READY   |   3    |
| ALERT_RUNNING |   4    |

Il **cambiamento di stato** varia secondo il seguente schema:

```mermaid
stateDiagram-v2
  [*] --> READY
  ERROR --> READY: KEEP_ALIVE
  READY --> ERROR: timeout
  READY --> RUNNING: START_REC, lettura
  RUNNING --> READY: END_REC
  RUNNING --> ALERT_RUNNING: dato >= MAX_TRESHOLD
  ALERT_RUNNING --> RUNNING: HANDLE_ALERT
  ALERT_RUNNING --> ALERT_READY: END_REC
  ALERT_READY --> READY: HANDLE_ALERT
  ALERT_READY --> ALERT_RUNNING: lettura
```

## NODO

Sul nodo (nel nostro caso un Rapsberry PI 2) gira uno script che si occupa di **gestire** i rilevatori.

Per maggiori informazioni consultare la [documentazione](./node/node.md).

## WEB-SERVICE E SALVATAGGIO DEI DATI

I due servizi principali che si occupano di memorizzazione ed elaborazione dei dati sono:

- `microservice_websocket`.
- `mock_mobius` (che simula la piattaforma **Mobius**).

In particolare, mentre `mock_mobius` si occupa soltanto di immagazzinare dati, `microservice_websocket` si occupa anche di **elaborarli** ed inviarli alla [ui](https://github.com/monemasrl/irma-ui.git) e di **inviare i comandi** ai nodi.

Per maggiori informazioni su **microservice_websocket** consultare la sua [documentazione](./microservice_websocket/microservice_websocket.md).

## TESTING IN LOCALE

Al fine di eseguire dei test in locale, per mancanza di rilevatori da utilizzare, viene usato lo script [mock_rilevatore.py](./utils/mock_rilevatore.py), che si occupa di **simulare** la presenza di un rilevatore.

Qualora vengano richieste delle letture dal **nodo**, lo script mostrerà un prompt dove inserire i valori da inviare.

### Struttura testing locale

```mermaid
flowchart LR; 
rpi4[Raspberry PI 4 - mock_rilevatore.py]
rpi2[Raspberry PI 2 - node]
msw[microservice_websocket]

rpi2 <-- CAN --> rpi4
rpi2 -- HTTP --> msw
msw -- MQTT --> rpi2
```

## CONTRIBUTING

Nella repo sono presenti i file di **configurazione per un pre-commit hook**, che avvia tool di *linting* e *formattazione*.

Per installare pre-commit: [sito ufficiale](https://pre-commit.com/).

Una volta installato basta eseguire:

```bash
$ pre-commit install
```

Per **installare gli hook** nella repo.
