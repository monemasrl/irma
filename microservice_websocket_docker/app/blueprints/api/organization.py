import json

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from ...utils.organization import create_organization, get_organizations

organization_bp = Blueprint("organization", __name__, url_prefix="/organizations")


@organization_bp.route("/", methods=["GET"])
@jwt_required()
def _get_organizations_route():
    organizations = get_organizations()

    if len(organizations) == 0:
        return {"message": "Not Found"}, 404

    return jsonify(organizations=organizations)


@organization_bp.route("/", methods=["POST"])
@jwt_required()
def _create_organization_route():
    record: dict = json.loads(request.data)

    organization = create_organization(record["name"])

    return organization.to_json()
