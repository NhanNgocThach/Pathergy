from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import family_schemas, models
from app.errors import ServiceError


def require_user(db: Session, user_id: int) -> models.UserAccount:
    user = db.get(models.UserAccount, user_id)
    if user is None:
        raise ServiceError(404, "USER_NOT_FOUND", "User account not found")
    return user


def create_user(
    db: Session,
    data: family_schemas.UserCreate,
) -> models.UserAccount:
    normalized_email = str(data.email).strip().casefold()
    existing_email = db.scalar(
        select(models.UserAccount).where(models.UserAccount.email == normalized_email)
    )
    if existing_email is not None:
        raise ServiceError(
            409,
            "USER_EMAIL_ALREADY_EXISTS",
            "A user with this email already exists",
        )

    if data.patient_id is not None:
        patient = db.get(models.Patient, data.patient_id)
        if patient is None:
            raise ServiceError(
                404,
                "USER_PROFILE_NOT_FOUND",
                "Patient profile not found",
            )
        existing_profile_owner = db.scalar(
            select(models.UserAccount).where(
                models.UserAccount.patient_id == data.patient_id
            )
        )
        if existing_profile_owner is not None:
            raise ServiceError(
                409,
                "USER_PROFILE_ALREADY_EXISTS",
                "This patient profile already belongs to a user",
            )
    else:
        patient = models.Patient(**data.profile.model_dump())
        db.add(patient)
        db.flush()

    user = models.UserAccount(
        email=normalized_email,
        display_name=data.display_name,
        patient_id=patient.id,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        message = str(error.orig).lower()
        if "patient_id" in message:
            raise ServiceError(
                409,
                "USER_PROFILE_ALREADY_EXISTS",
                "This patient profile already belongs to a user",
            ) from error
        raise ServiceError(
            409,
            "USER_EMAIL_ALREADY_EXISTS",
            "A user with this email already exists",
        ) from error
    db.refresh(user)
    return user


def get_profile(db: Session, user_id: int) -> models.Patient:
    user = require_user(db, user_id)
    patient = db.get(models.Patient, user.patient_id)
    if patient is None:
        raise ServiceError(
            404,
            "USER_PROFILE_NOT_FOUND",
            "Patient profile not found",
        )
    return patient
