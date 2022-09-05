import json

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from ...utils.application import create_application, get_applications
from ...utils.exceptions import (
    ObjectAttributeAlreadyUsedException,
    ObjectNotFoundException,
)

application_bp = Blueprint("application", __name__, url_prefix="/applications")


@application_bp.route("/<organizationID>", methods=["POST"])
@jwt_required()
def _create_application_route(organizationID):
    record: dict = json.loads(request.data)

    try:
        application = create_application(organizationID, record["name"])
    except ObjectNotFoundException:
        return {"message": "not found"}, 404
    except ObjectAttributeAlreadyUsedException:
        return {"message": "name already in use"}, 400

    return application.to_json()


@application_bp.route("/", methods=["GET"])
@jwt_required()
def _get_applications_route():
    organizationID: str = request.args.get("organizationID", "")

    if organizationID == "":
        return {"message": "Bad Request"}, 400

    try:
        applications = get_applications(organizationID)
    except ObjectNotFoundException:
        return {"message": "Not Found"}, 404

    return jsonify(applications=applications)
