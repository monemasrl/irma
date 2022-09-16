# Database [MongoDB](https://mongodb.com) di microservice_websocket

Il database ha più **collezioni**:

- User
- Role
- Organization
- Application
- Node
- Reading
- Alert

## User

Rappresenta l'**utente**.

I campi disponbili sono:

| Nome campo   | Tipo    | Note
| -            | -       | -
| email        | String  | max_length=255
| password     | String  | max_length=255
| first_name   | String  | default=''
| last_name    | String  | default=''
| roles        | List    | Reference(Role), default=[]

## Role

Rappresenta i **ruoli** che può avere l'**utente**.

I campi disponibili sono:

| Nome campo | Tipo  | Note
| -          | -     | -
| name       | String| max_length=80, unique=True
| description| String| max_length=255

## Organization

Rappresenta le **organizzazioni**.

I campi disponbili sono:

| Nome campo      | Tipo  | Note
| -               | -     | -
| organizationName| String| max_length=100, required=True

## Application

Rappresenta le **applicazioni**.

I campi disponibili sono:

| Nome campo     | Tipo     | Note
| -              | -        | -
| applicationName| String   | max_length=100, required=True
| organization   | Reference| Organization

## Node

Rappresenta il **nodo** dei sensori, presente in ogni staker.

I campi disponibili sono:

| Nome campo  | Tipo     | Note
| -           | -        | -
| nodeID      | String   | required=True
| nodeName    | String   | default='', required=True
| application | Reference| Application, required=True
| organization| Reference| Organization, required=True
| state       | Int      | required=True
| lastSeenAt  | Datetime | required=True

## Reading

Rappresenta una **lettura**.

I campi disponibili sono:

| Nome campo   | Tipo    | Note
| -            | -       | -
| nodeID       | Int     | required= True)
| canID        | Int     | required= True)
| sensorNumber | Int     | required= True)
| readingID    | Int     | required= True)
| sessionID    | Int     | required= True)
| dangerLevel  | Int     | default= 0)
| window1_count| Int     | default= 0)
| window2_count| Int     | default= 0)
| window3_count| Int     | default= 0)
| publishedAt  | DateTime| required= True)

## Alert

Rappresenta un'**allerta**.

I campi disponibili sono:

| Nome campo | Tipo     | Note
| -          | -        | -
| reading    | Reference| Reading, required=True
| node       | Reference| Node, required=True
| isHandled  | Boolean  | required=True
| isConfirmed| Boolean  |
| handledBy  | Reference| User
| handledAt  | DateTime |
| handleNote | String   |
