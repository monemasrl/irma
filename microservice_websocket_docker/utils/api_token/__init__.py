from functools import wraps
from flask import make_response, jsonify, request


def api_token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if "Authorization" not in request.headers:
            return make_response(jsonify({"message": "No API Token Provided"}), 401)

        token: str = request.headers["Authorization"].split(" ")[1]

        with open("./api-tokens.txt", "r") as file:
            tokens: list[str] = [x.strip() for x in file.readlines()]

            if token not in tokens:
                return make_response(jsonify({"message": "Invalid Token"}), 401)

        return f(*args, **kwargs)

    return decorator
