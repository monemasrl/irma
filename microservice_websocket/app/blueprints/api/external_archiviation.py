from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from ...utils.exceptions import ObjectNotFoundException
from ...utils.external_archiviation import (
    add_external_endpoint,
    delete_external_endpoint,
    get_external_endpoints,
)

ext_arch_bp = Blueprint(
    "external_archiviation", __name__, url_prefix="/external-archiviations"
)


@ext_arch_bp.route("/", methods=["GET"])
@jwt_required()
def get_external_endpoint_route():
    try:
        endpoints = get_external_endpoints()
    except ObjectNotFoundException:
        return {"message": "not found"}, 404

    return jsonify(endpoints=endpoints)


@ext_arch_bp.route("/add", methods=["POST"])
@jwt_required()
def add_external_endpoint_route():
    endpoint = request.json.get("endpoint", None)

    if endpoint is None:
        return {"message": "bad request"}, 400

    add_external_endpoint(endpoint)

    return {"message": "inserted"}, 200


@ext_arch_bp.route("/", methods=["DELETE"])
@jwt_required()
def delete_external_endpoint_route():
    endpoint = request.args.get("endpoint", None)

    if endpoint is None:
        return {"message": "bad request"}, 400

    try:
        delete_external_endpoint(endpoint)
    except ObjectNotFoundException:
        return {"message": "not found"}, 404

    return {"message": "deleted"}, 200
