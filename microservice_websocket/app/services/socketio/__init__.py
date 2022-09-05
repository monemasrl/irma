from flask import Flask
from flask_socketio import SocketIO


def init_socketio(socketio: SocketIO):
    @socketio.on("connect")
    def connected():
        print("Connected")

    @socketio.on("disconnect")
    def disconnected():
        print("Disconnected")

    @socketio.on("change")
    def onChange():
        print("Changed")
