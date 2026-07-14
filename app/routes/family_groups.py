from typing import Annotated

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app import family_schemas, models
from app.database import get_db
from app.routes.auth import get_current_user
from app.services import families

router = APIRouter(prefix="/family-groups", tags=["Family Groups"])
FamilyGroupId = Annotated[int, Path(ge=1)]
UserId = Annotated[int, Path(ge=1)]


@router.post("", response_model=family_schemas.FamilyGroupResponse, status_code=status.HTTP_201_CREATED)
def create_family_group(
    data: family_schemas.FamilyGroupCreate,
    db: Session = Depends(get_db),
    current_user: models.UserAccount = Depends(get_current_user),
):
    return families.create_family_group(db, data, current_user.user_id)


@router.get("/{family_group_id}", response_model=family_schemas.FamilyGroupResponse)
def get_family_group(
    family_group_id: FamilyGroupId,
    db: Session = Depends(get_db),
    current_user: models.UserAccount = Depends(get_current_user),
):
    return families.get_family_group(db, family_group_id, current_user.user_id)


@router.put("/{family_group_id}", response_model=family_schemas.FamilyGroupResponse)
def update_family_group(
    family_group_id: FamilyGroupId,
    data: family_schemas.FamilyGroupUpdate,
    db: Session = Depends(get_db),
    current_user: models.UserAccount = Depends(get_current_user),
):
    return families.update_family_group(
        db, family_group_id, data, current_user.user_id
    )


@router.post(
    "/{family_group_id}/members",
    response_model=family_schemas.MembershipResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_member(
    family_group_id: FamilyGroupId,
    data: family_schemas.MembershipCreate,
    db: Session = Depends(get_db),
    current_user: models.UserAccount = Depends(get_current_user),
):
    return families.add_member(db, family_group_id, data, current_user.user_id)


@router.get(
    "/{family_group_id}/members",
    response_model=list[family_schemas.MembershipResponse],
)
def list_members(
    family_group_id: FamilyGroupId,
    db: Session = Depends(get_db),
    current_user: models.UserAccount = Depends(get_current_user),
):
    return families.list_members(db, family_group_id, current_user.user_id)


@router.get(
    "/{family_group_id}/members/{user_id}",
    response_model=family_schemas.MembershipResponse,
)
def get_member(
    family_group_id: FamilyGroupId,
    user_id: UserId,
    db: Session = Depends(get_db),
    current_user: models.UserAccount = Depends(get_current_user),
):
    return families.get_member(db, family_group_id, user_id, current_user.user_id)


@router.put(
    "/{family_group_id}/members/{user_id}",
    response_model=family_schemas.MembershipResponse,
)
def update_member(
    family_group_id: FamilyGroupId,
    user_id: UserId,
    data: family_schemas.MembershipUpdate,
    db: Session = Depends(get_db),
    current_user: models.UserAccount = Depends(get_current_user),
):
    return families.update_member(
        db, family_group_id, user_id, data, current_user.user_id
    )


@router.post(
    "/{family_group_id}/members/{user_id}/leave",
    response_model=family_schemas.MembershipResponse,
)
def leave_group(
    family_group_id: FamilyGroupId,
    user_id: UserId,
    db: Session = Depends(get_db),
    current_user: models.UserAccount = Depends(get_current_user),
):
    return families.leave_group(
        db,
        family_group_id,
        user_id,
        current_user.user_id,
    )


@router.delete(
    "/{family_group_id}/members/{user_id}",
    response_model=family_schemas.MembershipResponse,
)
def remove_member(
    family_group_id: FamilyGroupId,
    user_id: UserId,
    db: Session = Depends(get_db),
    current_user: models.UserAccount = Depends(get_current_user),
):
    return families.remove_member(
        db,
        family_group_id,
        user_id,
        current_user.user_id,
    )


@router.get(
    "/{family_group_id}/members/{user_id}/permissions",
    response_model=list[family_schemas.PermissionResponse],
)
def get_permissions(
    family_group_id: FamilyGroupId,
    user_id: UserId,
    db: Session = Depends(get_db),
    current_user: models.UserAccount = Depends(get_current_user),
):
    return families.get_permissions(
        db,
        family_group_id,
        user_id,
        current_user.user_id,
    )


@router.put(
    "/{family_group_id}/members/{user_id}/permissions",
    response_model=list[family_schemas.PermissionResponse],
)
def update_permissions(
    family_group_id: FamilyGroupId,
    user_id: UserId,
    data: family_schemas.PermissionUpdate,
    db: Session = Depends(get_db),
    current_user: models.UserAccount = Depends(get_current_user),
):
    return families.update_permissions(
        db, family_group_id, user_id, data, current_user.user_id
    )
