from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

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
