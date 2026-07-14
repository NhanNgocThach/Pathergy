from typing import Literal

from sqlalchemy import select
from sqlalchemy.orm import Session, aliased

from app import family_schemas, models
from app.errors import ServiceError


def require_patient(db: Session, patient_id: int) -> models.Patient:
    patient = db.get(models.Patient, patient_id)
    if patient is None:
        raise ServiceError(404, "PATIENT_NOT_FOUND", "Patient not found")
    return patient


def _common_active_memberships(
    db: Session,
    requester_user_id: int,
    target_user_id: int,
) -> list[models.FamilyMembership]:
    requester_membership = aliased(models.FamilyMembership)
    return list(
        db.scalars(
            select(models.FamilyMembership)
            .join(
                requester_membership,
                requester_membership.family_group_id
                == models.FamilyMembership.family_group_id,
            )
            .where(
                models.FamilyMembership.user_id == target_user_id,
                models.FamilyMembership.status
                == family_schemas.MembershipStatus.active.value,
                requester_membership.user_id == requester_user_id,
                requester_membership.status
                == family_schemas.MembershipStatus.active.value,
            )
        )
    )


def require_patient_access(
    db: Session,
    patient_id: int,
    requester_user_id: int,
    data_type: family_schemas.FamilyDataType,
    action: Literal["view", "edit"],
) -> models.Patient:
    """Return a patient after checking ownership or family sharing permission."""
    patient = require_patient(db, patient_id)
    target_user = patient.user_account
    if target_user is not None and target_user.user_id == requester_user_id:
        return patient

    # Standalone profiles have no owner who can grant family access. Treat these
    # and unrelated profiles as not found so their existence is not disclosed.
    if target_user is None:
        raise ServiceError(404, "PATIENT_ACCESS_DENIED", "Patient not found")

    memberships = _common_active_memberships(
        db,
        requester_user_id,
        target_user.user_id,
    )
    if not memberships:
        raise ServiceError(404, "PATIENT_ACCESS_DENIED", "Patient not found")

    permission_column = (
        models.FamilyDataPermission.can_view
        if action == "view"
        else models.FamilyDataPermission.can_edit
    )
    allowed = db.scalar(
        select(models.FamilyDataPermission.permission_id).where(
            models.FamilyDataPermission.membership_id.in_(
                membership.membership_id for membership in memberships
            ),
            models.FamilyDataPermission.data_type == data_type.value,
            permission_column.is_(True),
        )
    )
    if allowed is None:
        raise ServiceError(
            403,
            "FAMILY_PERMISSION_DENIED",
            f"Family permission does not allow this {action} operation",
        )
    return patient


def require_medication_check_access(
    db: Session,
    patient_id: int,
    requester_user_id: int,
) -> models.Patient:
    patient = require_patient(db, patient_id)
    target_user = patient.user_account
    if target_user is not None and target_user.user_id == requester_user_id:
        return patient
    if target_user is None:
        raise ServiceError(404, "PATIENT_ACCESS_DENIED", "Patient not found")

    memberships = _common_active_memberships(
        db,
        requester_user_id,
        target_user.user_id,
    )
    if not memberships:
        raise ServiceError(404, "PATIENT_ACCESS_DENIED", "Patient not found")

    for membership in memberships:
        permissions = {
            permission.data_type: permission
            for permission in membership.permissions
        }
        allergy_permission = permissions.get(
            family_schemas.FamilyDataType.allergies.value
        )
        history_permission = permissions.get(
            family_schemas.FamilyDataType.screening_history.value
        )
        if (
            allergy_permission is not None
            and allergy_permission.can_view
            and history_permission is not None
            and history_permission.can_edit
        ):
            return patient

    raise ServiceError(
        403,
        "FAMILY_PERMISSION_DENIED",
        "Medication checks require allergy view and screening-history edit permission",
    )


def list_accessible_patients(
    db: Session,
    requester_user_id: int,
) -> list[models.Patient]:
    requester_membership = aliased(models.FamilyMembership)
    target_membership = aliased(models.FamilyMembership)
    shared_patient_ids = select(models.UserAccount.patient_id).join(
        target_membership,
        target_membership.user_id == models.UserAccount.user_id,
    ).join(
        requester_membership,
        requester_membership.family_group_id == target_membership.family_group_id,
    ).join(
        models.FamilyDataPermission,
        models.FamilyDataPermission.membership_id
        == target_membership.membership_id,
    ).where(
        target_membership.status == family_schemas.MembershipStatus.active.value,
        requester_membership.user_id == requester_user_id,
        requester_membership.status == family_schemas.MembershipStatus.active.value,
        models.FamilyDataPermission.data_type
        == family_schemas.FamilyDataType.basic_profile.value,
        models.FamilyDataPermission.can_view.is_(True),
    )
    own_patient_id = select(models.UserAccount.patient_id).where(
        models.UserAccount.user_id == requester_user_id
    )
    accessible_ids = own_patient_id.union(shared_patient_ids)
    return list(
        db.scalars(
            select(models.Patient)
            .where(models.Patient.id.in_(accessible_ids))
            .order_by(models.Patient.id)
        )
    )
