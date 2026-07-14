from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app import family_schemas, models, schemas
from app.auth_config import AuthSettings, get_auth_settings
from app.database import get_db
from app.errors import ServiceError
from app.routes.auth import get_current_user
from app.services import accounts, authorization, families

router = APIRouter(prefix="/users", tags=["Development Accounts"])
UserId = Annotated[int, Path(ge=1)]


@router.post("", response_model=family_schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    data: family_schemas.UserCreate,
    db: Session = Depends(get_db),
    current_user: models.UserAccount = Depends(get_current_user),
    settings: AuthSettings = Depends(get_auth_settings),
):
    if not settings.development_mode:
        raise ServiceError(404, "DEVELOPMENT_ENDPOINT_DISABLED", "Endpoint not found")
    return accounts.create_user(db, data)


@router.get("/{user_id}", response_model=family_schemas.UserResponse)
def get_user(
    user_id: UserId,
    db: Session = Depends(get_db),
    current_user: models.UserAccount = Depends(get_current_user),
):
    if user_id != current_user.user_id:
        raise ServiceError(404, "USER_ACCESS_DENIED", "User account not found")
    return accounts.require_user(db, user_id)


@router.get("/{user_id}/profile", response_model=schemas.PatientResponse)
def get_user_profile(
    user_id: UserId,
    db: Session = Depends(get_db),
    current_user: models.UserAccount = Depends(get_current_user),
):
    user = accounts.require_user(db, user_id)
    return authorization.require_patient_access(
        db,
        user.patient_id,
        current_user.user_id,
        family_schemas.FamilyDataType.basic_profile,
        "view",
    )


@router.get(
    "/{user_id}/family-groups",
    response_model=list[family_schemas.UserFamilyGroupResponse],
)
def list_user_family_groups(
    user_id: UserId,
    db: Session = Depends(get_db),
    current_user: models.UserAccount = Depends(get_current_user),
):
    if user_id != current_user.user_id:
        raise ServiceError(404, "USER_ACCESS_DENIED", "User account not found")
    return families.list_user_family_groups(db, user_id)
