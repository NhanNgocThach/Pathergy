from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Importing models registers every table with SQLAlchemy.
from app import models
from app.cors_config import get_cors_allowed_origins
from app.errors import ServiceError, service_error_handler, validation_error_handler
from app.routes import (
    allergies,
    auth,
    family_groups,
    medication_checks,
    medications,
    patients,
    users,
)
from app.security import add_security_headers, maximum_request_body_bytes


app = FastAPI(
    title="Pathergy API",
    version="6.1.0",
    description=(
        "An educational API for fictional patient records and standardized "
        "RxNorm medication information and conservative allergy screening. "
        "It is an educational prototype with authenticated personal accounts, "
        "ownership checks, and family sharing controls. It does not provide "
        "medical advice."
    ),
)

cors_allowed_origins = get_cors_allowed_origins()
if cors_allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_allowed_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )

app.add_exception_handler(ServiceError, service_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)


@app.middleware("http")
async def enforce_request_limits_and_security_headers(
    request: Request,
    call_next,
):
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            body_size = int(content_length)
        except ValueError:
            response = JSONResponse(
                status_code=400,
                content={
                    "detail": {
                        "code": "INVALID_CONTENT_LENGTH",
                        "message": "Content-Length must be a valid integer",
                    }
                },
            )
            add_security_headers(request, response)
            return response
        if body_size < 0 or body_size > maximum_request_body_bytes():
            response = JSONResponse(
                status_code=413,
                content={
                    "detail": {
                        "code": "REQUEST_TOO_LARGE",
                        "message": "Request body exceeds the configured limit",
                    }
                },
            )
            add_security_headers(request, response)
            return response

    response = await call_next(request)
    add_security_headers(request, response)
    return response

app.include_router(patients.router)
app.include_router(allergies.router)
app.include_router(medications.router)
app.include_router(medication_checks.router)
app.include_router(users.router)
app.include_router(family_groups.router)
app.include_router(auth.router)


@app.get("/", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"message": "Pathergy API is running"}


@app.get("/health", tags=["Health"], include_in_schema=False)
def deployment_health_check() -> dict[str, str]:
    """Small unauthenticated probe for cloud hosting health checks."""
    return {"status": "ok"}
