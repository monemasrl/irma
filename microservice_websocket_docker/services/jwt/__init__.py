from flask_jwt_extended import JWTManager
from services.database import user_manager


def init_jwt(app):
    jwt = JWTManager(app)

    # Register a callback function that takes whatever object is passed in as the
    # identity when creating JWTs and converts it to a JSON serializable format.
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        app.logger.info(f"Looking up: {user=}")
        return user_manager.get_user(user["email"])

    # Register a callback function that loads a user from your database whenever
    # a protected route is accessed. This should return any python object on a
    # successful lookup, or None if the lookup failed for any reason (for example
    # if the user has been deleted from the database).
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        app.logger.info(f"{identity=}")
        return user_manager.get_user(identity["email"])
