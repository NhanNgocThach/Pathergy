from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class ServiceError(Exception):
    """A predictable service-layer error with a stable API code."""

    def __init__(self, status_code: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message


async def service_error_handler(request: Request, error: ServiceError) -> JSONResponse:
    headers: dict[str, str] = {}
    if error.code in {
        "AUTHENTICATION_REQUIRED",
        "INVALID_ACCESS_TOKEN",
        "ACCESS_TOKEN_EXPIRED",
    }:
        headers["WWW-Authenticate"] = "Bearer"
    if error.status_code == 429:
        headers["Retry-After"] = "60"
    return JSONResponse(
        status_code=error.status_code,
        content={"detail": {"code": error.code, "message": error.message}},
        headers=headers,
    )


async def validation_error_handler(
    request: Request,
    error: RequestValidationError,
) -> JSONResponse:
    """Give new family enum errors stable codes; preserve FastAPI's other errors."""
    errors = error.errors()
    stable_codes = {
        "INVALID_FAMILY_ROLE",
        "INVALID_FAMILY_RELATIONSHIP",
        "INVALID_MEMBERSHIP_STATUS",
        "INVALID_PERMISSION_TYPE",
    }
    stable_error = next(
        (item for item in errors if item.get("type") in stable_codes),
        None,
    )
    if stable_error is not None:
        return JSONResponse(
            status_code=422,
            content={
                "detail": {
                    "code": stable_error["type"],
                    "message": stable_error["msg"],
                }
            },
        )
    return JSONResponse(
        status_code=422,
        content={"detail": jsonable_encoder(errors)},
    )
