from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from ...utils.admin import admin_required
from ...utils.exceptions import ObjectNotFoundException
from ...utils.user import (
    create_user,
    delete_user,
    get_user_info,
    get_user_list,
    update_user,
)

user_bp = Blueprint("blueprint", __name__, url_prefix="/user")


@user_bp.route("/list", methods=["GET"])
@jwt_required()
@admin_required
def get_user_list_route():
    users = get_user_list()

    return jsonify(users=users)


@user_bp.route("/<user_id>", methods=["GET"])
@jwt_required()
@admin_required
def get_user_info_route(user_id: str):
    user = get_user_info(user_id)

    if user is None:
        return {"msg": "Not Found"}, 404

    return jsonify(user.serialize())


@user_bp.route("/create", methods=["POST"])
@jwt_required()
@admin_required
def create_user_route():
    payload = request.json

    if payload is None:
        return {"msg": "Bad Request"}, 400

    for field in ["email", "password", "role"]:
        if field not in payload:
            return {"msg": f"Bad Request: missing field {field}"}, 400

    if not create_user(payload):
        return {"msg": "Already Existing User"}, 400

    return {"msg": "Created"}, 200


@user_bp.route("/<user_id>", methods=["PUT"])
@jwt_required()
def update_user_route(user_id: str):
    current_user = get_jwt_identity()

    if current_user["role"] != "admin" and current_user["id"] != user_id:
        return {"msg": "Unauthorized"}, 401

    payload = request.json

    if payload is None:
        return {"msg": "Bad Request"}, 400

    for field in ["email", "newPassword", "oldPassword", "role"]:
        if field not in payload:
            return {"msg": f"Bad Request: missing field {field}"}, 400

    try:
        if not update_user(user_id, payload):
            return {"msg": "Old Password Doesn't Match"}, 401
    except ObjectNotFoundException:
        return {"msg": "Not Found"}, 404

    return {"msg": "Updated"}, 200


@user_bp.route("/<user_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_user_route(user_id: str):
    current_user = get_jwt_identity()

    if current_user["id"] == user_id:
        return {"msg": "Cannot Delete Current Active User"}, 400

    try:
        delete_user(user_id)
    except ObjectNotFoundException:
        return {"msg": "Not Found"}, 404

    return {"msg": "Deleted"}, 200


@user_bp.route("/info", methods=["GET"])
@jwt_required()
def get_self_user_info_route():
    user_id = get_jwt_identity()["id"]

    user = get_user_info(user_id)

    if user is None:
        return {"msg": "Not Found"}, 404

    return jsonify(user.serialize())
