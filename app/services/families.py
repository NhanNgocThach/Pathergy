from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import family_schemas, models
from app.errors import ServiceError
from app.services.accounts import require_user


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def require_family_group(db: Session, family_group_id: int) -> models.FamilyGroup:
    group = db.get(models.FamilyGroup, family_group_id)
    if group is None:
        raise ServiceError(
            404,
            "FAMILY_GROUP_NOT_FOUND",
            "Family group not found",
        )
    return group


def active_membership(
    db: Session,
    family_group_id: int,
    user_id: int,
) -> models.FamilyMembership | None:
    return db.scalar(
        select(models.FamilyMembership).where(
            models.FamilyMembership.family_group_id == family_group_id,
            models.FamilyMembership.user_id == user_id,
            models.FamilyMembership.status
            == family_schemas.MembershipStatus.active.value,
        )
    )


def latest_membership(
    db: Session,
    family_group_id: int,
    user_id: int,
) -> models.FamilyMembership | None:
    current = active_membership(db, family_group_id, user_id)
    if current is not None:
        return current
    return db.scalar(
        select(models.FamilyMembership)
        .where(
            models.FamilyMembership.family_group_id == family_group_id,
            models.FamilyMembership.user_id == user_id,
        )
        .order_by(models.FamilyMembership.membership_id.desc())
    )


def require_active_membership(
    db: Session,
    family_group_id: int,
    user_id: int,
) -> models.FamilyMembership:
    membership = active_membership(db, family_group_id, user_id)
    if membership is None:
        raise ServiceError(
            403,
            "FAMILY_ACCESS_DENIED",
            "An active family membership is required",
        )
    return membership


def require_manager(
    db: Session,
    family_group_id: int,
    user_id: int,
) -> models.FamilyMembership:
    membership = require_active_membership(db, family_group_id, user_id)
    if membership.role not in {
        family_schemas.FamilyRole.owner.value,
        family_schemas.FamilyRole.admin.value,
    }:
        raise ServiceError(
            403,
            "FAMILY_ACCESS_DENIED",
            "An OWNER or ADMIN membership is required",
        )
    return membership


def add_default_permissions(
    db: Session,
    membership: models.FamilyMembership,
) -> None:
    for data_type in family_schemas.FamilyDataType:
        db.add(
            models.FamilyDataPermission(
                membership_id=membership.membership_id,
                data_type=data_type.value,
                can_view=False,
                can_edit=False,
            )
        )


def create_family_group(
    db: Session,
    data: family_schemas.FamilyGroupCreate,
) -> models.FamilyGroup:
    require_user(db, data.requesting_user_id)
    group = models.FamilyGroup(
        name=data.name,
        created_by_user_id=data.requesting_user_id,
    )
    db.add(group)
    db.flush()
    membership = models.FamilyMembership(
        family_group_id=group.family_group_id,
        user_id=data.requesting_user_id,
        role=family_schemas.FamilyRole.owner.value,
        relationship_type=family_schemas.FamilyRelationship.self.value,
        status=family_schemas.MembershipStatus.active.value,
        joined_at=utc_now(),
    )
    db.add(membership)
    db.flush()
    add_default_permissions(db, membership)
    db.commit()
    db.refresh(group)
    return group


def get_family_group(
    db: Session,
    family_group_id: int,
    requesting_user_id: int,
) -> models.FamilyGroup:
    group = require_family_group(db, family_group_id)
    require_active_membership(db, family_group_id, requesting_user_id)
    return group


def update_family_group(
    db: Session,
    family_group_id: int,
    data: family_schemas.FamilyGroupUpdate,
) -> models.FamilyGroup:
    group = require_family_group(db, family_group_id)
    require_manager(db, family_group_id, data.requesting_user_id)
    if data.name is not None:
        group.name = data.name
    if data.is_active is not None:
        group.is_active = data.is_active
    db.commit()
    db.refresh(group)
    return group


def list_user_family_groups(
    db: Session,
    user_id: int,
    requesting_user_id: int,
) -> list[dict[str, object]]:
    require_user(db, user_id)
    if requesting_user_id != user_id:
        raise ServiceError(
            403,
            "FAMILY_ACCESS_DENIED",
            "Users may view only their own family memberships",
        )
    memberships = list(
        db.scalars(
            select(models.FamilyMembership)
            .where(models.FamilyMembership.user_id == user_id)
            .order_by(models.FamilyMembership.membership_id)
        )
    )
    return [
        {
            "family_group": membership.family_group,
            "membership": membership,
        }
        for membership in memberships
    ]


def add_member(
    db: Session,
    family_group_id: int,
    data: family_schemas.MembershipCreate,
) -> models.FamilyMembership:
    require_family_group(db, family_group_id)
    require_manager(db, family_group_id, data.requesting_user_id)
    require_user(db, data.user_id)

    open_membership = db.scalar(
        select(models.FamilyMembership).where(
            models.FamilyMembership.family_group_id == family_group_id,
            models.FamilyMembership.user_id == data.user_id,
            models.FamilyMembership.status.in_(
                [
                    family_schemas.MembershipStatus.pending.value,
                    family_schemas.MembershipStatus.active.value,
                ]
            ),
        )
    )
    if open_membership is not None:
        raise ServiceError(
            409,
            "DUPLICATE_ACTIVE_MEMBERSHIP",
            "The user already has an active or pending membership in this group",
        )

    membership = models.FamilyMembership(
        family_group_id=family_group_id,
        user_id=data.user_id,
        role=data.role.value,
        relationship_type=data.relationship.value,
        status=family_schemas.MembershipStatus.pending.value,
    )
    db.add(membership)
    db.flush()
    add_default_permissions(db, membership)
    db.commit()
    db.refresh(membership)
    return membership


def list_members(
    db: Session,
    family_group_id: int,
    requesting_user_id: int,
) -> list[models.FamilyMembership]:
    require_family_group(db, family_group_id)
    require_active_membership(db, family_group_id, requesting_user_id)
    return list(
        db.scalars(
            select(models.FamilyMembership)
            .where(models.FamilyMembership.family_group_id == family_group_id)
            .order_by(models.FamilyMembership.membership_id)
        )
    )


def get_member(
    db: Session,
    family_group_id: int,
    user_id: int,
    requesting_user_id: int,
) -> models.FamilyMembership:
    require_family_group(db, family_group_id)
    require_active_membership(db, family_group_id, requesting_user_id)
    membership = latest_membership(db, family_group_id, user_id)
    if membership is None:
        raise ServiceError(
            404,
            "FAMILY_MEMBERSHIP_NOT_FOUND",
            "Family membership not found",
        )
    return membership


def active_owner_count(db: Session, family_group_id: int) -> int:
    return db.scalar(
        select(func.count(models.FamilyMembership.membership_id)).where(
            models.FamilyMembership.family_group_id == family_group_id,
            models.FamilyMembership.role == family_schemas.FamilyRole.owner.value,
            models.FamilyMembership.status
            == family_schemas.MembershipStatus.active.value,
        )
    ) or 0


def protect_last_owner(
    db: Session,
    membership: models.FamilyMembership,
    new_role: str,
    new_status: str,
) -> None:
    stops_being_owner = (
        membership.role == family_schemas.FamilyRole.owner.value
        and membership.status == family_schemas.MembershipStatus.active.value
        and (
            new_role != family_schemas.FamilyRole.owner.value
            or new_status != family_schemas.MembershipStatus.active.value
        )
    )
    if stops_being_owner and active_owner_count(db, membership.family_group_id) <= 1:
        raise ServiceError(
            409,
            "LAST_OWNER_CANNOT_LEAVE",
            "Transfer ownership before changing the final active OWNER",
        )


def update_member(
    db: Session,
    family_group_id: int,
    user_id: int,
    data: family_schemas.MembershipUpdate,
) -> models.FamilyMembership:
    require_family_group(db, family_group_id)
    require_manager(db, family_group_id, data.requesting_user_id)
    membership = latest_membership(db, family_group_id, user_id)
    if membership is None:
        raise ServiceError(404, "FAMILY_MEMBERSHIP_NOT_FOUND", "Family membership not found")
    if membership.status not in {
        family_schemas.MembershipStatus.pending.value,
        family_schemas.MembershipStatus.active.value,
    }:
        raise ServiceError(409, "MEMBERSHIP_NOT_ACTIVE", "Membership is no longer open")

    new_role = data.role.value if data.role is not None else membership.role
    new_status = data.status.value if data.status is not None else membership.status
    allowed_statuses = {
        family_schemas.MembershipStatus.pending.value: {
            family_schemas.MembershipStatus.pending.value,
            family_schemas.MembershipStatus.active.value,
            family_schemas.MembershipStatus.declined.value,
        },
        family_schemas.MembershipStatus.active.value: {
            family_schemas.MembershipStatus.active.value,
        },
    }
    if new_status not in allowed_statuses[membership.status]:
        raise ServiceError(
            422,
            "INVALID_MEMBERSHIP_STATUS",
            "Use the leave or remove endpoint for an active membership",
        )

    protect_last_owner(db, membership, new_role, new_status)
    if new_status == family_schemas.MembershipStatus.active.value:
        duplicate = active_membership(db, family_group_id, user_id)
        if duplicate is not None and duplicate.membership_id != membership.membership_id:
            raise ServiceError(
                409,
                "DUPLICATE_ACTIVE_MEMBERSHIP",
                "The user already has an active membership in this group",
            )
        if membership.joined_at is None:
            membership.joined_at = utc_now()
    elif new_status == family_schemas.MembershipStatus.declined.value:
        membership.left_at = utc_now()

    membership.role = new_role
    membership.status = new_status
    if data.relationship is not None:
        membership.relationship_type = data.relationship.value
    db.commit()
    db.refresh(membership)
    return membership


def leave_group(
    db: Session,
    family_group_id: int,
    user_id: int,
    requesting_user_id: int,
) -> models.FamilyMembership:
    require_family_group(db, family_group_id)
    if requesting_user_id != user_id:
        raise ServiceError(403, "FAMILY_ACCESS_DENIED", "A user may leave only for themselves")
    membership = active_membership(db, family_group_id, user_id)
    if membership is None:
        raise ServiceError(409, "MEMBERSHIP_NOT_ACTIVE", "Membership is not active")
    protect_last_owner(
        db,
        membership,
        membership.role,
        family_schemas.MembershipStatus.left.value,
    )
    membership.status = family_schemas.MembershipStatus.left.value
    membership.left_at = utc_now()
    db.commit()
    db.refresh(membership)
    return membership


def remove_member(
    db: Session,
    family_group_id: int,
    user_id: int,
    requesting_user_id: int,
) -> models.FamilyMembership:
    require_family_group(db, family_group_id)
    require_manager(db, family_group_id, requesting_user_id)
    membership = latest_membership(db, family_group_id, user_id)
    if membership is None:
        raise ServiceError(404, "FAMILY_MEMBERSHIP_NOT_FOUND", "Family membership not found")
    if membership.status not in {
        family_schemas.MembershipStatus.pending.value,
        family_schemas.MembershipStatus.active.value,
    }:
        raise ServiceError(409, "MEMBERSHIP_NOT_ACTIVE", "Membership is no longer open")
    protect_last_owner(
        db,
        membership,
        membership.role,
        family_schemas.MembershipStatus.removed.value,
    )
    membership.status = family_schemas.MembershipStatus.removed.value
    membership.left_at = utc_now()
    db.commit()
    db.refresh(membership)
    return membership


def require_own_active_membership(
    db: Session,
    family_group_id: int,
    user_id: int,
    requesting_user_id: int,
) -> models.FamilyMembership:
    require_family_group(db, family_group_id)
    if requesting_user_id != user_id:
        raise ServiceError(
            403,
            "PERMISSION_ACCESS_DENIED",
            "Users control permissions only for their own membership",
        )
    membership = active_membership(db, family_group_id, user_id)
    if membership is None:
        raise ServiceError(
            403,
            "MEMBERSHIP_NOT_ACTIVE",
            "An active membership is required to manage permissions",
        )
    return membership


def get_permissions(
    db: Session,
    family_group_id: int,
    user_id: int,
    requesting_user_id: int,
) -> list[models.FamilyDataPermission]:
    membership = require_own_active_membership(
        db,
        family_group_id,
        user_id,
        requesting_user_id,
    )
    return list(
        db.scalars(
            select(models.FamilyDataPermission)
            .where(models.FamilyDataPermission.membership_id == membership.membership_id)
            .order_by(models.FamilyDataPermission.permission_id)
        )
    )


def update_permissions(
    db: Session,
    family_group_id: int,
    user_id: int,
    data: family_schemas.PermissionUpdate,
) -> list[models.FamilyDataPermission]:
    membership = require_own_active_membership(
        db,
        family_group_id,
        user_id,
        data.requesting_user_id,
    )
    existing = {
        permission.data_type: permission
        for permission in db.scalars(
            select(models.FamilyDataPermission).where(
                models.FamilyDataPermission.membership_id == membership.membership_id
            )
        )
    }
    for permission_data in data.permissions:
        permission = existing[permission_data.data_type.value]
        permission.can_view = permission_data.can_view
        permission.can_edit = permission_data.can_edit
    db.commit()
    return get_permissions(db, family_group_id, user_id, data.requesting_user_id)
