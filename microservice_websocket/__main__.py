import microservice_websocket

app, socketio = microservice_websocket.create_app()
socketio.run(app, debug=True, host="0.0.0.0")
