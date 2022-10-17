# microservice_websocket

Questo servizio si occupa di interfacciarsi con la piattaforma **Mobius** (vedi [mock_mobius](../mock_mobius_docker)), con il database [MongoDB](https://mongodb.com) e con la dashboard.

## Avvio

L'**immagine docker** può essere avviata con il file [docker-compose.yaml](../docker-compose.yaml) presente nella **root della repo**.

## Configurazione

Sono presenti due file di configurazione, uno relativo al [webserver](./config/config_server.json) in sé per sé, l'altro relativo al [comportamento dell'applicazione](./config/config.json).

> :warning: **Relativo al [webserver](./config/config_server.json)**: Ricordarsi di generare una nuova Secret Key!

### [config.json](./config/config.json)

```jsonc
{
  // Tempo di cache delle letture prima
  // di essere inviate al servizio di
  // backup esterno (Mobius)
  "READING_SYNC_WAIT": 60,

  // Ogni quanto controllare che il tempo
  // di cache sia passato
  "CHECK_SYNC_READY": 30,

  // Intervallo di timeout del nodo
  "NODE_TIMEOUT_INTERVAL": 30,

  // Ogni quanto controllare che i
  // nodi non siano in timeout
  "NODE_TIMEOUT_CHECK_INTERVAL": 10,

  // soglia che fa scattare lo stato di Alert
  "ALERT_TRESHOLD": 7
}
```

## Descrizione API

### Richiesta sessione di letture (GET /api/session/)

È possibile **richiedere** una sessione di letture mediante una **GET** su **/api/session/**.

Sono disponibili i seguenti **parametri**:

- `nodeID`: l'**id** del **nodo** di cui si richiede la **sessione**.
- `sessionID`: l'**id** della **sessione**. Se non presente o uguale a -1, verr à restituita la sessione più **recente**.

---

Corpo della **risposta**:

- `readings`: un array di [Reading](./app/services/database/database.md#reading), conformi al metodo `serialize()` della classe.

Esempio:

```jsonc
{
  "readings": [{}, {}, {}]
}
```

### Richiesta id sessioni (GET /api/session/ids)

È possibile **richiedere** gli **id** delle sessioni di un certo **nodo** mediante una **GET** su **/api/session/ids**.

Sono disponibili i seguenti **parametri**:

- `nodeID`: l'**id** del **nodo** di cui si richiede la **lista degli id**.

---

Corpo della **risposta**:

- `IDs`: un array di **interi**, che rappresentano gli **id** delle **sessioni disponibli** per quel **nodo**.

Esempio:

```jsonc
{
  "IDs": [123, 456, 789]
}
```

### Pubblicazione dati (POST /api/payload/publish)

È possibile **pubblicare** dei dati mediante una **POST** su **/api/payload/publish**.

A differenza delle altre route che sono protette da **Token JWT**, questa è protetta da un **API Token** statico (si consiglia un **UUID**) che deve essere **inserito** all'interno di `microservice_websocket/api-tokens.txt`.

Corpo della richiesta:

```jsonc
{
  "nodeID": 1,
  "nodeName": "irma-node",
  "applicationID": "foo",
  "organizationID": "bar",
  "payloadType": 1, // Fare riferimento agli Enum
  "data": {
      "canID": 3,
      "sensorNumber": 4.5,
      "value": 2,
      "count": 1345,
      "sessionID": 7,
      "readingID": 3
  }
}
```

> Per maggiori info su **PayloadType** fare riferimento gli [enum](../README.md#gli-enum).

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

Il dato viene poi immagazzinato all'interno del **database** come [Reading](./app/services/database/database.md#reading).

### Invio comandi al nodo (POST /api/payload/command)

È possibile inviare comandi al nodo mediante una **POST** su **/api/payload/command**.

Corpo della richiesta (JSON):

- `command`: il comando da inviare al **nodo**. [Per maggiori informazioni](../README.md#gli-enum).
- `applicationID`: l'**id** dell'**applicazione** di cui fa parte il **nodo**.
- `nodeID`: l'**id** del **nodo** a cui inviare il comando.

Esempio:

```jsonc
{
  "command": 0,
  "applicationID": "13244",
  "nodeID": 1
}
```

---

A questo punto **microservice_websocket** pubblicherà sul **topic** `<applicationID>/<nodeID>/command` un **payload** contenente un [CommandType](../README.md#gli-enum).

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

Per maggiori informazioni sulla struttura dell'[Alert](./app/services/database/database.md#alert).

### Info Alert (GET /api/alert/info)

Per ottenere maggiori **informazioni** su di un **Alert**, è possibile effettuare una **GET** su **/api/alert/info**.

Sono disponibili i seguenti **parametri**:

- `id`: l'**id** dell'**Alert** di cui si richiedon le **informazioni**.

---

Corpo della **risposta**:

- `nodeID`: l'**id** del **Node** a cui fa riferimento l'**Alert**.
- `sessionID`: l'**id** della **session** a cui fa riferimento l'**Alert**.
- `readingID`: l'**id** della **Reading** che ha generato l'**Alert**.
- `canID`: l'**id** del **rilevatore** che ha generato l'**Alert**.
- `alertID`: l'**id** dell'**Alert**.
- `raisedAt`: il **UNIX timestamp** relativo a quando è stato generato l'**Alert**.

Esempio:

```jsonc
{
  "nodeID": 1,
  "sessionID": 1640400,
  "readingID": 1640800,
  "canID": 3,
  "alertID": "63186eab0ca2d54a5c258384",
  "raisedAt": 1640830
}
```

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

Ogni **elemento** all'interno della **lista** è conforme alla struttura [Organization](./app/services/database/database.md#organization).

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

- `organizationID`: l'**id** dell'**organizzazione** a cui appartengono le **applicazioni**.

Corpo della risposta (JSON):

- `applications`: la **lista** delle **applicazioni**.

Ogni **elemento** all'interno della **lista** è conforme alla struttura [Application](./app/services/database/database.md#application).

Esempio:
```jsonc
{
  "applications": [{}, {}, {}]
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

### Lista dei nodi (GET /api/nodes/)

Per ottenere la lista dei **nodi** è necessario fare una **GET** su **/api/nodes/**.

Sono disponibili i seguenti **parametri**:

- `applicationID`: l'**id** dell'**applicazione** a cui devono appartenere i **sensori**.

Corpo della risposta (JSON):

- `nodes`: la **lista** dei **nodi**.

Ogni **elemento** all'interno della **lista** è conforme alla struttura del metodo `to_dashboard()` del **Node**.

Esempio:
```jsonc
{
  "nodes": [{}, {}, {}]
}
```

### Lista endpoint di archiviazione esterna (GET /api/external-archiviations/)

Per ottenere la lista degli **endpoint** di archiviazione esterna è necessario fare una **GET** su **/api/external-archiviations/**.

Corpo della risposta (JSON):

- `endpoints`: **array di stringhe** contenente gli endpoint **inseriti**.

Esempio:
```jsonc
{
  "endpoints": ["http://localhost:3000"]
}
```

### Aggiunta endpoint di archiviazione esterna (POST /api/external-archiviations/add)

Per **aggiungere** un **endpoint** è necessario fare una **POST** su **/api/external-archiviations/add**.

Corpo della richiesta (JSON):

- `endpoint`: **stringa** contenente l'url dell'endpoint.

Esempio:
```jsonc
{
  "endpoint": "http://localhost:3000"
}
```

### Rimozione endpoint di archiviazione esterna (DELETE /api/external-archivitions/)

Per **eliminare** un **endpoint** è necessario fare una **DELETE** su **/api/external-archiviations/**.

Sono disponibili i seguenti parametri:

- `endpoint`: stringa contenente l'endpoint da **eliminare**.
