from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

# Importing models registers every table with SQLAlchemy.
from app import models
from app.errors import ServiceError, service_error_handler, validation_error_handler
from app.routes import (
    allergies,
    family_groups,
    medication_checks,
    medications,
    patients,
    users,
)


app = FastAPI(
    title="Pathergy API",
    version="5.0.0",
    description=(
        "An educational API for fictional patient records and standardized "
        "RxNorm medication information and conservative allergy screening. "
        "It is an educational prototype with development-only personal accounts "
        "and family sharing controls. It does not provide medical advice."
    ),
)

app.add_exception_handler(ServiceError, service_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)

app.include_router(patients.router)
app.include_router(allergies.router)
app.include_router(medications.router)
app.include_router(medication_checks.router)
app.include_router(users.router)
app.include_router(family_groups.router)


@app.get("/", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"message": "Pathergy API is running"}
