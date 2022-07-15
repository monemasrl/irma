# microservice_websocket

Questo servizio si occupa di interfacciarsi con la piattaforma **Mobius** (vedi [mock_mobius](../mock_mobius_docker)) e con la dashboard.

## Avvio

Nel [docker-compose.yaml](../docker-compose.yaml) presente nella **root della repo**, microservice_websocket viene fatto partire **insieme** a tutti gli altri serivizi.

Nel caso in cui si volesse avviare **standalone**, viene fornito il file **docker-compose.yaml** all'interno della cartella [microservice_websocket_docker](./docker-compose.yaml).

Per i comandi di **docker-compose** fare riferimento al paragrafo **DEPLOYMENT** nel [README](../README.md).

## Configurazione tramite variabili d'ambiente

È possibile specificare le seguenti opzioni tramite variabili d'ambiente:

- **MAX_TRESHOLD**: valore della soglia di pericolo dei sensori, default `20`.
- **MOBIUS_URL**: l'indirizzo dell'istanza Mobius, default `http://localhost`.
- **MOBIUS_PORT**: la porta su cui è esposto il servizio, default `5002`.
- **DISABLE_MQTT**: disabilita il servizio MQTT per il testing, True se settato ad 1, default False.
- **MQTT_BROKER_URL**: url del serivizo MQTT per comunicare con Chirpstack, default `localhost`.
- **MQTT_BROKER_PORT**: porta del servizio MQTT per comunicare con Chirpstackm default `1883`.

## Descrizione API

### Richiesta dati (POST /)

È possibile **richiedere** dati mediante una **POST** su **/**. 

Corpo della **richiesta** (JSON):

- `paths`: un array che contiene tutti i **sensor_paths** che si vogliono richiedere a **Mobius**.

Esempio:

```jsonc
{
  "paths": [
    "01203",
    "21332"
  ]
}
```

---

**microservice_websocket** procederà a fare una richiesta **GET** su **/<SENSOR_PATH>** a **Mobius** per ogni sensor_path ricevuto.

Corpo della **risposta**:

- `devEUI`: il **deviceEUI** del sensore.
- `applicationID`: l'**applicationID** di cui fa parte il sensore.
- `sensorId`: l'**id** del sensore.
- `state`: lo **stato** del sensore. Le opzioni possibili sono: `off`, `ok`, `rec` e `alert`.
- `datiInterni`: **array di dati** da visualizzare nella dashboard.
    
Ogni elemento all'interno di `datiInerni` ha i seguenti attributi:

- `titolo`: **titolo** del dato.
- `dato`: il **dato**.

Esempio:

```jsonc
{
  "devEUI": "AgICAgICAgI=",
  "applicationID": "1",
  "sensorId": "LORA_sensor_01",
  "state": "ok",
  "datiInterni": [
    {
      "titolo": "Titolo1",
      "dato": 123
    },
    {
      "titolo": "Titolo2",
      "dato": 456
    },
    {
      "titolo": "Titolo3",
      "dato": 789
    }
  ]
}
```

### Pubblicazione dati (POST /publish)

È possibile **pubblicare** dei dati mediante una **POST** su **/publish**.

Il corpo della richiesta è quello che viene inviato di default da [Chirpstack](https://www.chirpstack.io/application-server/), con l'**aggiunta** di **due parametri**.

Esempio di **richiesta**:

```jsonc
{
  "applicationID": "1",
  "applicationName": "irma",
  "deviceName": "irma-sensor",
  "devEUI": "AgICAgICAgI=",
  "rxInfo": [
    {
      "gatewayID": "e45f01fffe7da7a8",
      "time": null,
      "timeSinceGPSEpoch": null,
      "rssi": -61,
      "loRaSNR": -2.8,
      "channel": 7,
      "rfChain": 0,
      "board": 0,
      "antenna": 0,
      "location": {
        "latitude": 45.7,
        "longitude": 32.9,
        "altitude": 0,
        "source": "UNKNOWN",
        "accuracy": 0
      },
      "fineTimestampType": "NONE",
      "context": "XZ4gbA==",
      "uplinkID": "76d9f46d-d799-491e-ac16-48f953077232",
      "crcStatus": "CRC_OK"
    }
  ],
  "txInfo": {
    "frequency": 867900000,
    "modulation": "LORA",
    "loRaModulationInfo": {
      "bandwidth": 125,
      "spreadingFactor": 12,
      "codeRate": "4/5",
      "polarizationInversion": false
    }
  },
  "adr": true,
  "dr": 0,
  "fCnt": 6,
  "fPort": 2,
  "data": "ABE=",
  "objectJSON": {
    "sensorData": 17
  },
  "tags": {
    "sensorId": "LORA_sensor_01",
    "sensor_path": "283923423"
  },
  "confirmedUplink": true,
  "devAddr": "0021051c",
  "publishedAt": "2013-03-31T16:21:17.528002Z",
  "deviceProfileID": "be018f1b-c068-43c0-a276-a7665ff090b4",
  "deviceProfileName": "device-OTAA"
}
```

L'aggiunta dei parametri deve essere effettuata dalla **dashboard di chirpstack**, sotto la sezione **tags** del **Device**.

---

A questo punto la funzione `to_mobius_payload`, all'interno di [app.py](./app.py), convertirà il **payload** e lo invierà a **Mobius**.

Il **payload** che viene inviato a **Mobius** ha questa forma:

```jsonc
{
  "m2m:cin": {
    "con": {
      "metadata": {
        "sensorId": "LORA_sensor_01",
        "readingTimestamp": "2013-03-31T16:21:17.528002Z",
        "latitude": 45.7,
        "longitude": 32.7
      }
    },
    "sensorData": {} // l'intero payload di Chirpstack
  }
}
```

### Invio segnale di downlink (POST /downlink)

È possibiale inviare una richiesta di downlink mediante una **POST** su **/downlink**.

Corpo della richiesta (JSON):

- `statoStaker`: indica il segnale da inviare al sensore: `1` corrisponde a `start` e `0` corrsponde a `stop`.
- `applicationID`: l'ID dell'applicazione di cui fa parte il sensore.
- `devEUI`: il deviceEUI del sensore a cui inviare il segnale (non decodificato).

Esempio:

```jsonc
{
  "statoStaker": 1,
  "applicationID": "1",
  "devEUI": "AgICAgICAgI="
}
```

A questo punto **microservice_websocket** invierà il segnale di **downlink** a Chirpstack tramite **MQTT**.
