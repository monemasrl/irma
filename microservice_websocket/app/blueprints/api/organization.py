import json

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from ...utils.exceptions import ObjectNotFoundException
from ...utils.organization import create_organization, get_organizations

organization_bp = Blueprint("organization", __name__, url_prefix="/organizations")


@organization_bp.route("/", methods=["GET"])
@jwt_required()
def _get_organizations_route():
    try:
        organizations = get_organizations()
    except ObjectNotFoundException:
        return {"message": "Not Found"}, 404

    return jsonify(organizations=organizations)


@organization_bp.route("/", methods=["POST"])
@jwt_required()
def _create_organization_route():
    record: dict = json.loads(request.data)
    name = record.get("name", None)

    if name is None:
        return {"message": "Bad Request"}, 400

    try:
        organization = create_organization(name)
    except ObjectNotFoundException:
        return {"message": f"""name '{record["name"]}' is already in use"""}, 400

    return organization.to_json()
