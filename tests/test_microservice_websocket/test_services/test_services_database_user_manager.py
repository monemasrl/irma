from microservice_websocket.app.services.database import User, user_manager


def test_password_hashing():
    password = "verysecret"
    hash = user_manager.hash_password(password)

    user = User(email="foo@bar.com", password=hash, first_name="Bob", last_name="Noss")

    assert user_manager.verify(user, password) and not user_manager.verify(
        user, "baz"
    ), "Error in password hashing"
