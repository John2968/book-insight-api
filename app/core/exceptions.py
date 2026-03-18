from fastapi import HTTPException, status

from app.schemas.common import ErrorDetail, ErrorResponse


def http_error(status_code: int, code: str, message: str, details: dict | None = None) -> HTTPException:
    return HTTPException(
        status_code=status_code,
        detail=ErrorResponse(error=ErrorDetail(code=code, message=message, details=details)).model_dump(),
    )


def not_found(code: str, message: str = "Resource not found", details: dict | None = None) -> HTTPException:
    return http_error(status.HTTP_404_NOT_FOUND, code=code, message=message, details=details)


def bad_request(code: str, message: str, details: dict | None = None) -> HTTPException:
    return http_error(status.HTTP_400_BAD_REQUEST, code=code, message=message, details=details)


def forbidden(code: str, message: str = "Forbidden", details: dict | None = None) -> HTTPException:
    return http_error(status.HTTP_403_FORBIDDEN, code=code, message=message, details=details)


def unauthorized(code: str = "AUTH_ERROR", message: str = "Could not validate credentials") -> HTTPException:
    return http_error(
        status.HTTP_401_UNAUTHORIZED,
        code=code,
        message=message,
    )

