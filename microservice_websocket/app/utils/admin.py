from functools import wraps

from flask import jsonify, make_response
from flask_jwt_extended import get_jwt_identity


def admin_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        user = get_jwt_identity()

        if not user["role"] == "admin":
            return make_response(jsonify({"msg": "Unauthorized"}), 401)

        return f(*args, **kwargs)

    return decorator
