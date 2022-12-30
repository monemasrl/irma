from fastapi import HTTPException, status


class DuplicateException(HTTPException):
    def __init__(self, field_name: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Duplicate field '{field_name}'",
        )


class NotFoundException(HTTPException):
    def __init__(self, detail: str | None = None):
        detail = "Not found" if detail is None else f"'{detail}' not found"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
