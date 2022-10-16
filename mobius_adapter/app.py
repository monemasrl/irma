from flask import Flask, request

from utils import insert


def create_app():
    app = Flask(__name__)

    @app.route("/", methods=["POST"])
    def receive_payload():
        payload = request.json

        try:
            insert(payload)
        except KeyError:
            return {"message": "bad request"}, 400

        return {"message": "forwarded"}, 200

    return app
