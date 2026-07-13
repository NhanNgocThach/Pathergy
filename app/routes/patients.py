from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Response, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import get_db
from app.errors import ServiceError

router = APIRouter(prefix="/patients", tags=["Patients"])
PatientId = Annotated[int, Path(ge=1)]


def require_patient(db: Session, patient_id: int) -> models.Patient:
    patient = crud.get_patient(db, patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.post("", response_model=schemas.PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(
    patient_data: schemas.PatientCreate,
    db: Session = Depends(get_db),
) -> models.Patient:
    return crud.create_patient(db, patient_data)


@router.get("", response_model=list[schemas.PatientResponse])
def list_patients(db: Session = Depends(get_db)) -> list[models.Patient]:
    return crud.list_patients(db)


@router.get("/{patient_id}", response_model=schemas.PatientResponse)
def get_patient(patient_id: PatientId, db: Session = Depends(get_db)) -> models.Patient:
    return require_patient(db, patient_id)


@router.put("/{patient_id}", response_model=schemas.PatientResponse)
def update_patient(
    patient_id: PatientId,
    patient_data: schemas.PatientUpdate,
    db: Session = Depends(get_db),
) -> models.Patient:
    patient = require_patient(db, patient_id)
    return crud.update_patient(db, patient, patient_data)


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(patient_id: PatientId, db: Session = Depends(get_db)) -> Response:
    patient = require_patient(db, patient_id)
    if patient.user_account is not None:
        raise ServiceError(
            409,
            "PERSONAL_PROFILE_DELETE_FORBIDDEN",
            "A user-owned personal profile cannot be deleted through patient CRUD",
        )
    crud.delete_patient(db, patient)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
