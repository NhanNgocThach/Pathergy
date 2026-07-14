from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.database import get_db
from app.family_schemas import FamilyDataType
from app.routes.auth import get_current_user
from app.routes.medications import get_rxnorm_service
from app.services import authorization
from app.services.rxnorm import (
    IncompleteRxNormResponseError,
    MedicationNotFoundError,
    RxNormService,
    RxNormTimeoutError,
    RxNormUnavailableError,
)
from app.services.screening import find_allergy_matches

router = APIRouter(prefix="/patients", tags=["Medication Checks"])
PatientId = Annotated[int, Path(ge=1)]


@router.post(
    "/{patient_id}/medication-check",
    response_model=schemas.MedicationCheckResponse,
    responses={404: {"description": "Patient not found"}},
)
def check_medication(
    patient_id: PatientId,
    check_request: schemas.MedicationCheckRequest,
    db: Session = Depends(get_db),
    rxnorm_service: RxNormService = Depends(get_rxnorm_service),
    current_user: models.UserAccount = Depends(get_current_user),
) -> schemas.MedicationCheckResponse:
    authorization.require_medication_check_access(
        db, patient_id, current_user.user_id
    )
    allergies = crud.list_allergies(db, patient_id)

    try:
        medication = rxnorm_service.search_medication(check_request.medication_name)
    except (
        MedicationNotFoundError,
        RxNormTimeoutError,
        RxNormUnavailableError,
        IncompleteRxNormResponseError,
    ):
        return unable_to_verify_response(
            db=db,
            patient_id=patient_id,
            medication_name=check_request.medication_name,
        )

    matches = find_allergy_matches(allergies, medication.active_ingredients)
    if matches:
        result = schemas.MedicationCheckResult.potential_allergy_match
        message = "One or more recorded allergies match a listed active ingredient."
    elif not medication.ingredient_data_complete or not medication.active_ingredients:
        result = schemas.MedicationCheckResult.unable_to_verify
        message = "The medication's active ingredients could not be fully confirmed."
    else:
        result = schemas.MedicationCheckResult.no_recorded_match_found
        message = "No listed active ingredient matched the patient's recorded allergies."

    history = crud.create_search_history(
        db=db,
        patient_id=patient_id,
        medication_name=check_request.medication_name,
        normalized_medication_name=medication.normalized_name,
        medication_rxcui=medication.rxcui,
        result=result,
    )
    return schemas.MedicationCheckResponse(
        history_id=history.id,
        patient_id=patient_id,
        medication_query=check_request.medication_name,
        normalized_medication_name=medication.normalized_name,
        medication_rxcui=medication.rxcui,
        active_ingredients=medication.active_ingredients,
        result=result,
        matches=matches,
        message=message,
    )


@router.get(
    "/{patient_id}/screening-history",
    response_model=list[schemas.SearchHistoryResponse],
)
def list_screening_history(
    patient_id: PatientId,
    db: Session = Depends(get_db),
    current_user: models.UserAccount = Depends(get_current_user),
) -> list[models.SearchHistory]:
    authorization.require_patient_access(
        db,
        patient_id,
        current_user.user_id,
        FamilyDataType.screening_history,
        "view",
    )
    return crud.list_search_history(db, patient_id)


def unable_to_verify_response(
    db: Session,
    patient_id: int,
    medication_name: str,
) -> schemas.MedicationCheckResponse:
    result = schemas.MedicationCheckResult.unable_to_verify
    history = crud.create_search_history(
        db=db,
        patient_id=patient_id,
        medication_name=medication_name,
        result=result,
    )
    return schemas.MedicationCheckResponse(
        history_id=history.id,
        patient_id=patient_id,
        medication_query=medication_name,
        normalized_medication_name=None,
        medication_rxcui=None,
        active_ingredients=[],
        result=result,
        matches=[],
        message="The medication and its active ingredients could not be confirmed.",
    )
