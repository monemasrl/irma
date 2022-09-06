# microservice_websocket

Questo servizio si occupa di interfacciarsi con la piattaforma **Mobius** (vedi [mock_mobius](../mock_mobius_docker)), con il database [MongoDB](https://mongodb.com) e con la dashboard.

## Avvio

Nel [docker-compose.yaml](../docker-compose.yaml) presente nella **root della repo**, microservice_websocket viene fatto partire **insieme** a tutti gli altri serivizi.

Nel caso in cui lo si volesse avviare **standalone**, viene fornito il file **docker-compose.yaml** all'interno della cartella [microservice_websocket](./docker-compose.yaml).

Per i comandi di **docker-compose** fare riferimento al paragrafo **DEPLOYMENT** nel [README](../README.md).

## Configurazione

All'interno del file [config.json](./config/config.json) è possibile specificare una serie di opzioni.

## Descrizione API

### Richiesta dati (POST /api/payload/)

È possibile **richiedere** dati mediante una **POST** su **/api/payload/**.

Corpo della **richiesta** (JSON):

- `IDs`: un array che contiene tutti i **sensorID** che si vogliono richiedere.

Esempio:

```jsonc
{
  "IDs": [
    "01203",
    "21332"
  ]
}
```

---

**microservice_websocket** procederà ad interrogare il **database** per ogni **sensorID** ricevuto.

Corpo della **risposta**:

- `sensorID`: l'**id** del sensore.
- `sensorName`: il **nome** del sensore.
- `applicationID`: l'**id** dell'applicazione a cui appartiene il sensore.
- `state`: lo **stato** del sensore. Fare riferimento al paragrafo sugli **Enum** nel [README](../README.md).
- `datiInterni`: **array di dati** da visualizzare nella dashboard.
- `unhandledAlertIDs`: gli **id** delle **allerte non gestite**.

Ogni elemento all'interno di `datiInerni` ha i seguenti attributi:

- `titolo`: **titolo** del dato.
- `dato`: il **dato**.

Esempio:

```jsonc
{
  "sensorID": "1",
  "sensorName": "sensore_1",
  "applicationID": "34375765",
  "state": 1,
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
  ],
  "unhandledAlertIDs": [
    "123"
  ]
}
```

### Pubblicazione dati (POST /api/payload/publish)

È possibile **pubblicare** dei dati mediante una **POST** su **/api/payload/publish**.

A differenza delle altre route che sono protette da **Token JWT**, questa è protetta da un **API Token** statico (si consiglia un **UUID**) che deve essere **inserito** all'interno di *microservice_websocket/api-tokens.txt*.

Il corpo della richiesta può essre di due tipi:

- Quello inviato dal [nodo](../node/app.py).
- Quello inviato di default da [Chirpstack](https://www.chirpstack.io/application-server/).

> Le richieste di **chirpstack** vengono convertite a richieste del **nodo**.

Esempio di **richiesta** dal **nodo**:

```jsonc
{
  "sensorID": 1,
  "applicationID": "foo",
  "organizationID": "bar",
  "deviceName": "irma-sensor",
  "data": {
      "state": 3,
      "sensorData": 4.5,
      "mobius_sensorId": "foo",
      "mobius_sensorPath": "bar",
  },
  "publishedAt": "time", // iso8601 timestamp
  "payloadType": 1
}
```

---

La funzione `to_mobius_payload`, all'interno di [mobius/utils.py](./app/services/mobius/utils.py), convertirà il **payload** e lo invierà a **Mobius**.

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

---

Il dato viene poi immagazzinato all'interno del **database** come **Reading**. Per maggiori informazioni sul database fare riferimento alla [documentazione](./app/services/database/database.md).

### Invio comandi al sensore (POST /api/payload/command)

È possibile inviare comandi al sensore mediante una **POST** su **/api/payload/command**.

Corpo della richiesta (JSON):

- `command`: il comando da inviare al **sensore**. Per maggiori informazioni fare riferimento al paragrafo sugli **Enum** del [README](../README.md).
- `applicationID`: l'**id** dell'**applicazione** di cui fa parte il **sensore**.
- `sensorID`: l'**id** del **sensore** a cui inviare il comando.

Esempio:

```jsonc
{
  "command": 0,
  "applicationID": "13244",
  "sensorID": 1
}
```

---

A questo punto **microservice_websocket** pubblicherà sul **topic** `<applicationID>/<sensorID>/command` un **payload**.

Per maggior informazioni sulla struttura del **payload**, fare riferimento al paragrafo **Encode e decode dei dati** del [README](../README.md).

### Gestion alert (POST /api/alert/handle)

È possibile **gestire** un **alert** mediante una **POST** su **/api/alert/handle**.

Corpo della richiesta (JSON):

- `alertID`: l'**id** dell'**alert**.
- `isConfirmed`: **boolean**, indica se l'operatore **conferma** o no l'**alert**.
- `handleNote`: **messaggio** abbinato alla gestione.

Esempio:

```jsonc
{
  "alertID": "13244",
  "isConfirmed": false,
  "handleNote": "Falso allarme"
}
```

---

A questo punto **microservice_websocket** registrerà l'**alert** come **gestita**, registrando anche:

- l'**utente** che l'ha gestita.
- se l'utente **conferma** l'**alert**.
- **quando** l'ha gestita.
- le eventuali **note**.

Per maggior informazioni sulla struttura del **alert** nel database, fare riferimento alla sua [documentazione](./app/services/database/database.md).

### Autenticazione (POST /api/jwt/authenticate)

Per effettuare l'**autenticazione** ed ottene un **Token JWT** e il relativo **Token JWT di refresh**, è necessario effettuare una **POST** su **/api/jwt/authenticate**.

Corpo della richiesta (JSON):

- `username`
- `password`

Esempio:

```jsonc
{
  "username": "foo",
  "password": "bar"
}
```

---

Nel caso in cui l'**utente** sia **registrato** otterà come risposta il **Token JWT** e il relativo **Token JWT di refresh**, altrimenti 401, `{ "message": "wrong username or password" }`.

Corpo della risposta (JSON):

- `access_token`: il **Token JWT**.
- `refresh_token`: il **Token JWT di refresh**.

Esempio:

```jsonc
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
}
```

### Refresh (POST /api/jwt/refresh)

Per **refreshare** il **Token JWT** è possibile effettuare una **POST** su **/api/jwt/refresh**.

Se il **Token JWT di refresh** non è valido, il server risponderà con un 401.

Corpo della risposta (JSON):

- `access_token`: il **Token JWT**.

Esempio:

```jsonc
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
}
```

### Lista organizzazioni (GET /api/organizations/)

Per ottenere la lista delle **organizzazioni** è necessario fare una **GET** su **/api/organizations/**.

Corpo della risposta (JSON):

- `organizations`: la **lista** delle **organizzazioni**.

Ogni **elemento** all'interno della **lista** è conforme alla struttura **Organization** all'interno del **database**. Per maggior informazioni fare riferimento alla [documentazione](./app/services/database/database.md).

Esempio:
```jsonc
{
  "organizations": [{}, {}, {}]
}
```

### Creazione organizzazione (POST /api/organizations/)

Per **creare** un'organizzazione è necessario fare una **POST** su **/api/organizations/**.

Nel caso in cui il nome dell'organizzazione sia **già in uso**, il server risponderà con un errore `400`.

Corpo della richiesta (JSON):

- `name`: il **nome** dell'organizzazione da creare.

Esempio:
```jsonc
{
  "name": "organizzazione1"
}
```

### Lista applicazioni (GET /api/applications/)

Per ottenere la lista delle **applicazioni** è necessario fare una **GET** su **/api/applications/**.

Sono disponibili i seguenti **parametri**:

- `organizationID`: l'**id** dell'**organizzazione** a cui devono appartenere le **applicazioni** (**OBBLIGATORIO**).

Corpo della risposta (JSON):

- `applications`: la **lista** delle **applicazioni**.

Ogni **elemento** all'interno della **lista** è conforme alla struttura **Application** all'interno del **database**. Per maggior informazioni fare riferimento alla [documentazione](./app/services/database/database.md).

Esempio:
```jsonc
{
  "applications": [ {}, {}, {}]
}
```

### Creazione applicazione (POST /api/applications/\<organizationID\>)

Per **creare** un'applicazione è necessario fare una **POST** su **/api/applications/\<organizationID\>**.

Nel caso in cui l'**id** organizzazione **non corrisponda** ad alcuna organizzazione **esistente**, il server risponderà con un error `404`.

Nel caso in cui il nome dell'applicazione sia **già in uso**, il server risponderà con un errore `400`.

Corpo della richiesta (JSON):

- `name`: il **nome** dell'organizzazione da creare.

Esempio:
```jsonc
{
  "name": "organizzazione1"
}
```

### Lista dei sensori (GET /api/sensors/)

Per ottenere la lista dei **sensori** è necessario fare una **GET** su **/api/sensors/**.

Sono disponibili i seguenti **parametri**:

- `applicationID`: l'**id** dell'**applicazione** a cui devono appartenere i **sensori** (**OBBLIGATORIO**).

Corpo della risposta (JSON):

- `sensors`: la **lista** dei **sensori**.

Ogni **elemento** all'interno della **lista** è conforme alla struttura **Application** all'interno del **database**. Per maggior informazioni fare riferimento alla [documentazione](./app/services/database/database.md).

Esempio:
```jsonc
{
  "applications": [ {}, {}, {}]
}
```
