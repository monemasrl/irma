from flask import Flask
from flask_socketio import SocketIO


def create_socketio(app: Flask) -> SocketIO:
    socketio: SocketIO = SocketIO(app, cors_allowed_origins="*")

    @socketio.on("connect")
    def connected():
        print("Connected")

    @socketio.on("disconnect")
    def disconnected():
        print("Disconnected")

    @socketio.on("change")
    def onChange():
        print("Changed")

    return socketio
