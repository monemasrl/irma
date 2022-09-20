from flask import Blueprint, jsonify

from microservice_websocket.app.utils.api_token import api_token_required

test_bp = Blueprint("test", __name__, url_prefix="/test")


@test_bp.route("/api-token-test")
@api_token_required
def api_token_test():
    return jsonify({"message": "Valid API Token!"})
