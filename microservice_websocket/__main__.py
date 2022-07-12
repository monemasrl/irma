import microservice_websocket

app, socketio = microservice_websocket.create_app()
socketio.run(
    app,
    debug=True,
    host=microservice_websocket.HOST,
    port=microservice_websocket.PORT
)
