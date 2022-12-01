from fastapi import HTTPException, status


def verify_api_token(token: str | None):
    invalid_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token"
    )

    if token is None:
        raise invalid_token_exception

    try:
        token = token.split(" ")[1]
    except IndexError:
        raise invalid_token_exception

    with open("./api-tokens.txt", "r") as file:
        tokens: list[str] = [x.strip() for x in file.readlines()]

        if token not in tokens:
            raise invalid_token_exception
