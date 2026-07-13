from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app import family_schemas, schemas
from app.database import get_db
from app.services import accounts, families

router = APIRouter(prefix="/users", tags=["Development Accounts"])
UserId = Annotated[int, Path(ge=1)]
RequestingUserId = Annotated[int, Query(ge=1)]


@router.post("", response_model=family_schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    data: family_schemas.UserCreate,
    db: Session = Depends(get_db),
):
    return accounts.create_user(db, data)


@router.get("/{user_id}", response_model=family_schemas.UserResponse)
def get_user(user_id: UserId, db: Session = Depends(get_db)):
    return accounts.require_user(db, user_id)


@router.get("/{user_id}/profile", response_model=schemas.PatientResponse)
def get_user_profile(user_id: UserId, db: Session = Depends(get_db)):
    return accounts.get_profile(db, user_id)


@router.get(
    "/{user_id}/family-groups",
    response_model=list[family_schemas.UserFamilyGroupResponse],
)
def list_user_family_groups(
    user_id: UserId,
    requesting_user_id: RequestingUserId,
    db: Session = Depends(get_db),
):
    return families.list_user_family_groups(db, user_id, requesting_user_id)
