from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from microservice_websocket.app.utils.api_token import api_token_required

test_bp = Blueprint("test", __name__, url_prefix="/test")


@test_bp.route("/api-token-test")
@api_token_required
def api_token_test():
    return jsonify({"message": "Valid API Token!"})


@test_bp.route("/jwt-test")
@jwt_required()
def jwttest():
    return jsonify({"foo": "bar", "baz": "qux"})
