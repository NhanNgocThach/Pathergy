from typing import Annotated

from fastapi import APIRouter, Depends, Path, Response, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.auth_config import AuthSettings, get_auth_settings
from app.database import get_db
from app.errors import ServiceError
from app.family_schemas import FamilyDataType
from app.routes.auth import get_current_user
from app.services import authorization

router = APIRouter(prefix="/patients", tags=["Patients"])
PatientId = Annotated[int, Path(ge=1)]

@router.post("", response_model=schemas.PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(
    patient_data: schemas.PatientCreate,
    db: Session = Depends(get_db),
    current_user: models.UserAccount = Depends(get_current_user),
    settings: AuthSettings = Depends(get_auth_settings),
) -> models.Patient:
    if not settings.development_mode:
        raise ServiceError(404, "DEVELOPMENT_ENDPOINT_DISABLED", "Endpoint not found")
    return crud.create_patient(db, patient_data)


@router.get("", response_model=list[schemas.PatientResponse])
def list_patients(
    db: Session = Depends(get_db),
    current_user: models.UserAccount = Depends(get_current_user),
) -> list[models.Patient]:
    return authorization.list_accessible_patients(db, current_user.user_id)


@router.get("/{patient_id}", response_model=schemas.PatientResponse)
def get_patient(
    patient_id: PatientId,
    db: Session = Depends(get_db),
    current_user: models.UserAccount = Depends(get_current_user),
) -> models.Patient:
    return authorization.require_patient_access(
        db, patient_id, current_user.user_id, FamilyDataType.basic_profile, "view"
    )


@router.put("/{patient_id}", response_model=schemas.PatientResponse)
def update_patient(
    patient_id: PatientId,
    patient_data: schemas.PatientUpdate,
    db: Session = Depends(get_db),
    current_user: models.UserAccount = Depends(get_current_user),
) -> models.Patient:
    patient = authorization.require_patient_access(
        db, patient_id, current_user.user_id, FamilyDataType.basic_profile, "edit"
    )
    return crud.update_patient(db, patient, patient_data)


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(
    patient_id: PatientId,
    db: Session = Depends(get_db),
    current_user: models.UserAccount = Depends(get_current_user),
) -> Response:
    patient = authorization.require_patient_access(
        db, patient_id, current_user.user_id, FamilyDataType.basic_profile, "edit"
    )
    if patient.user_account is not None:
        raise ServiceError(
            409,
            "PERSONAL_PROFILE_DELETE_FORBIDDEN",
            "A user-owned personal profile cannot be deleted through patient CRUD",
        )
    crud.delete_patient(db, patient)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
