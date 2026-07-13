from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Response, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import get_db
from app.routes.patients import require_patient

router = APIRouter(prefix="/patients/{patient_id}/allergies", tags=["Allergies"])
PatientId = Annotated[int, Path(ge=1)]
AllergyId = Annotated[int, Path(ge=1)]


def duplicate_allergy_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="This patient already has an allergy record for that substance",
    )


def require_allergy(db: Session, patient_id: int, allergy_id: int) -> models.Allergy:
    allergy = crud.get_allergy(db, patient_id, allergy_id)
    if allergy is None:
        raise HTTPException(status_code=404, detail="Allergy record not found")
    return allergy


@router.post(
    "",
    response_model=schemas.AllergyResponse,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"description": "Duplicate allergy substance for this patient"}},
)
def create_allergy(
    patient_id: PatientId,
    allergy_data: schemas.AllergyCreate,
    db: Session = Depends(get_db),
) -> models.Allergy:
    require_patient(db, patient_id)
    try:
        return crud.create_allergy(db, patient_id, allergy_data)
    except crud.DuplicateAllergyError:
        raise duplicate_allergy_error()


@router.get("", response_model=list[schemas.AllergyResponse])
def list_allergies(
    patient_id: PatientId,
    db: Session = Depends(get_db),
) -> list[models.Allergy]:
    require_patient(db, patient_id)
    return crud.list_allergies(db, patient_id)


@router.get("/{allergy_id}", response_model=schemas.AllergyResponse)
def get_allergy(
    patient_id: PatientId,
    allergy_id: AllergyId,
    db: Session = Depends(get_db),
) -> models.Allergy:
    require_patient(db, patient_id)
    return require_allergy(db, patient_id, allergy_id)


@router.put(
    "/{allergy_id}",
    response_model=schemas.AllergyResponse,
    responses={409: {"description": "Duplicate allergy substance for this patient"}},
)
def update_allergy(
    patient_id: PatientId,
    allergy_id: AllergyId,
    allergy_data: schemas.AllergyUpdate,
    db: Session = Depends(get_db),
) -> models.Allergy:
    require_patient(db, patient_id)
    allergy = require_allergy(db, patient_id, allergy_id)
    try:
        return crud.update_allergy(db, allergy, allergy_data)
    except crud.DuplicateAllergyError:
        raise duplicate_allergy_error()


@router.delete("/{allergy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_allergy(
    patient_id: PatientId,
    allergy_id: AllergyId,
    db: Session = Depends(get_db),
) -> Response:
    require_patient(db, patient_id)
    allergy = require_allergy(db, patient_id, allergy_id)
    crud.delete_allergy(db, allergy)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
