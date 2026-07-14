from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas


class DuplicateAllergyError(Exception):
    """Raised when a patient already has an allergy for a substance."""


def handle_allergy_integrity_error(db: Session, error: IntegrityError) -> None:
    """Translate the expected unique-constraint error and preserve other errors."""
    db.rollback()
    database_message = str(error.orig).lower()
    sqlstate = getattr(error.orig, "sqlstate", None)
    if sqlstate == "23505" or "unique" in database_message:
        raise DuplicateAllergyError from error
    raise error


def create_patient(db: Session, patient_data: schemas.PatientCreate) -> models.Patient:
    patient = models.Patient(**patient_data.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def list_patients(db: Session) -> list[models.Patient]:
    return list(db.scalars(select(models.Patient).order_by(models.Patient.id)))


def get_patient(db: Session, patient_id: int) -> models.Patient | None:
    return db.get(models.Patient, patient_id)


def update_patient(
    db: Session,
    patient: models.Patient,
    patient_data: schemas.PatientUpdate,
) -> models.Patient:
    for field, value in patient_data.model_dump().items():
        setattr(patient, field, value)
    db.commit()
    db.refresh(patient)
    return patient


def delete_patient(db: Session, patient: models.Patient) -> None:
    db.delete(patient)
    db.commit()


def create_allergy(
    db: Session,
    patient_id: int,
    allergy_data: schemas.AllergyCreate,
) -> models.Allergy:
    allergy = models.Allergy(patient_id=patient_id, **allergy_data.model_dump())
    db.add(allergy)
    try:
        db.commit()
    except IntegrityError as error:
        handle_allergy_integrity_error(db, error)
    db.refresh(allergy)
    return allergy


def list_allergies(db: Session, patient_id: int) -> list[models.Allergy]:
    statement = (
        select(models.Allergy)
        .where(models.Allergy.patient_id == patient_id)
        .order_by(models.Allergy.id)
    )
    return list(db.scalars(statement))


def get_allergy(
    db: Session,
    patient_id: int,
    allergy_id: int,
) -> models.Allergy | None:
    statement = select(models.Allergy).where(
        models.Allergy.id == allergy_id,
        models.Allergy.patient_id == patient_id,
    )
    return db.scalar(statement)


def update_allergy(
    db: Session,
    allergy: models.Allergy,
    allergy_data: schemas.AllergyUpdate,
) -> models.Allergy:
    for field, value in allergy_data.model_dump().items():
        setattr(allergy, field, value)
    try:
        db.commit()
    except IntegrityError as error:
        handle_allergy_integrity_error(db, error)
    db.refresh(allergy)
    return allergy


def delete_allergy(db: Session, allergy: models.Allergy) -> None:
    db.delete(allergy)
    db.commit()


def create_search_history(
    db: Session,
    patient_id: int,
    medication_name: str,
    result: schemas.MedicationCheckResult,
    normalized_medication_name: str | None = None,
    medication_rxcui: str | None = None,
) -> models.SearchHistory:
    history = models.SearchHistory(
        patient_id=patient_id,
        medication_name=medication_name,
        normalized_medication_name=normalized_medication_name,
        medication_rxcui=medication_rxcui,
        result=result.value,
    )
    db.add(history)
    db.commit()
    db.refresh(history)
    return history


def list_search_history(db: Session, patient_id: int) -> list[models.SearchHistory]:
    return list(
        db.scalars(
            select(models.SearchHistory)
            .where(models.SearchHistory.patient_id == patient_id)
            .order_by(models.SearchHistory.id.desc())
        )
    )
