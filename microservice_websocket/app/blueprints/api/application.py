import json

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from ...utils.application import create_application, get_applications

application_bp = Blueprint("application", __name__, url_prefix="/applications")


@application_bp.route("/<organizationID>", methods=["POST"])
@jwt_required()
def _create_application_route(organizationID):
    record: dict = json.loads(request.data)

    application = create_application(organizationID, record["name"])

    if application is None:
        return {"message": "Not Found"}, 404

    return application.to_json()


@application_bp.route("/", methods=["GET"])
@jwt_required()
def _get_applications_route():
    organizationID: str = request.args.get("organizationID", "")

    if organizationID == "":
        return {"message": "Bad Request"}, 400

    applications = get_applications(organizationID)

    if len(applications) == 0:
        return {"message": "Not Found"}, 404

    return jsonify(applications=applications)
