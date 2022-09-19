from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required

from ...utils.user import get_user_info

user_bp = Blueprint("blueprint", __name__, url_prefix="/user")


@user_bp.route("/info", methods=["GET"])
@jwt_required()
def get_user_info_route():
    user_id = get_jwt_identity()["_id"]["$oid"]

    user = get_user_info(user_id)

    if user is None:
        return {"msg": "Not Found"}, 404

    return jsonify(user.to_json())
