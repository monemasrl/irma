import os

from flask import Flask, request

from utils import insert

TESTING = os.environ.get("TESTING", False)


def create_app():
    app = Flask(__name__)

    @app.route("/", methods=["POST"])
    def receive_payload():
        payload = request.json

        if TESTING:
            insert(payload)
        else:
            try:
                insert(payload)
            except KeyError:
                return {"message": "bad request"}, 400

        return {"message": "forwarded"}, 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)
