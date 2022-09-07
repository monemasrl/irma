from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from ...utils.exceptions import ObjectNotFoundException
from ...utils.node import get_nodes

node_bp = Blueprint("node", __name__, url_prefix="/nodes")


@node_bp.route("/", methods=["GET"])
@jwt_required()
def get_nodes_route():
    applicationID: str = request.args.get("applicationID", "")

    if applicationID == "":
        return {"message": "Bad Request"}, 400

    try:
        nodes = get_nodes(applicationID)
    except ObjectNotFoundException:
        return {"message": "Not Found"}, 404

    return jsonify(nodes=nodes)
