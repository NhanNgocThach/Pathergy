from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session

from app import family_schemas
from app.database import get_db
from app.services import families

router = APIRouter(prefix="/family-groups", tags=["Family Groups"])
FamilyGroupId = Annotated[int, Path(ge=1)]
UserId = Annotated[int, Path(ge=1)]
RequestingUserId = Annotated[int, Query(ge=1)]


@router.post("", response_model=family_schemas.FamilyGroupResponse, status_code=status.HTTP_201_CREATED)
def create_family_group(
    data: family_schemas.FamilyGroupCreate,
    db: Session = Depends(get_db),
):
    return families.create_family_group(db, data)


@router.get("/{family_group_id}", response_model=family_schemas.FamilyGroupResponse)
def get_family_group(
    family_group_id: FamilyGroupId,
    requesting_user_id: RequestingUserId,
    db: Session = Depends(get_db),
):
    return families.get_family_group(db, family_group_id, requesting_user_id)


@router.put("/{family_group_id}", response_model=family_schemas.FamilyGroupResponse)
def update_family_group(
    family_group_id: FamilyGroupId,
    data: family_schemas.FamilyGroupUpdate,
    db: Session = Depends(get_db),
):
    return families.update_family_group(db, family_group_id, data)


@router.post(
    "/{family_group_id}/members",
    response_model=family_schemas.MembershipResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_member(
    family_group_id: FamilyGroupId,
    data: family_schemas.MembershipCreate,
    db: Session = Depends(get_db),
):
    return families.add_member(db, family_group_id, data)


@router.get(
    "/{family_group_id}/members",
    response_model=list[family_schemas.MembershipResponse],
)
def list_members(
    family_group_id: FamilyGroupId,
    requesting_user_id: RequestingUserId,
    db: Session = Depends(get_db),
):
    return families.list_members(db, family_group_id, requesting_user_id)


@router.get(
    "/{family_group_id}/members/{user_id}",
    response_model=family_schemas.MembershipResponse,
)
def get_member(
    family_group_id: FamilyGroupId,
    user_id: UserId,
    requesting_user_id: RequestingUserId,
    db: Session = Depends(get_db),
):
    return families.get_member(db, family_group_id, user_id, requesting_user_id)


@router.put(
    "/{family_group_id}/members/{user_id}",
    response_model=family_schemas.MembershipResponse,
)
def update_member(
    family_group_id: FamilyGroupId,
    user_id: UserId,
    data: family_schemas.MembershipUpdate,
    db: Session = Depends(get_db),
):
    return families.update_member(db, family_group_id, user_id, data)


@router.post(
    "/{family_group_id}/members/{user_id}/leave",
    response_model=family_schemas.MembershipResponse,
)
def leave_group(
    family_group_id: FamilyGroupId,
    user_id: UserId,
    data: family_schemas.MembershipAction,
    db: Session = Depends(get_db),
):
    return families.leave_group(
        db,
        family_group_id,
        user_id,
        data.requesting_user_id,
    )


@router.delete(
    "/{family_group_id}/members/{user_id}",
    response_model=family_schemas.MembershipResponse,
)
def remove_member(
    family_group_id: FamilyGroupId,
    user_id: UserId,
    requesting_user_id: RequestingUserId,
    db: Session = Depends(get_db),
):
    return families.remove_member(
        db,
        family_group_id,
        user_id,
        requesting_user_id,
    )


@router.get(
    "/{family_group_id}/members/{user_id}/permissions",
    response_model=list[family_schemas.PermissionResponse],
)
def get_permissions(
    family_group_id: FamilyGroupId,
    user_id: UserId,
    requesting_user_id: RequestingUserId,
    db: Session = Depends(get_db),
):
    return families.get_permissions(
        db,
        family_group_id,
        user_id,
        requesting_user_id,
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
):
    return families.update_permissions(db, family_group_id, user_id, data)
