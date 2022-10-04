import json

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)

from ...services.database import user_manager

jwt_bp = Blueprint("jwt", __name__, url_prefix="/jwt")


# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@jwt_bp.route("/authenticate", methods=["POST"])
def authenticate():
    json_payload = json.loads(request.data)
    username = json_payload.get("username", None)
    password = json_payload.get("password", None)

    if username is None or password is None:
        return jsonify({"message": "Bad Request"}), 400

    user = user_manager.get_user(username)

    if user is None:
        return jsonify({"message": "User not found"}), 404

    if user_manager.verify(user, password):
        access_token = create_access_token(identity=user.serialize())
        refresh_token = create_refresh_token(identity=user.serialize())
        return jsonify(access_token=access_token, refresh_token=refresh_token)

    return jsonify({"message": "wrong username or password"}), 401


@jwt_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():
    identity = get_jwt_identity()
    print(type(identity))
    if identity is None:
        return {"message": "User Not Found"}, 401

    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token)
