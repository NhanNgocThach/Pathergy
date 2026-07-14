from datetime import datetime
from enum import Enum

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
    model_validator,
)
from pydantic_core import PydanticCustomError

from app.schemas import PatientCreate


class FamilyRole(str, Enum):
    owner = "OWNER"
    admin = "ADMIN"
    member = "MEMBER"


class FamilyRelationship(str, Enum):
    self = "SELF"
    spouse = "SPOUSE"
    child = "CHILD"
    parent = "PARENT"
    sibling = "SIBLING"
    relative = "RELATIVE"
    caregiver = "CAREGIVER"
    other = "OTHER"


class MembershipStatus(str, Enum):
    pending = "PENDING"
    active = "ACTIVE"
    left = "LEFT"
    removed = "REMOVED"
    declined = "DECLINED"


class FamilyDataType(str, Enum):
    basic_profile = "BASIC_PROFILE"
    allergies = "ALLERGIES"
    current_medications = "CURRENT_MEDICATIONS"
    screening_history = "SCREENING_HISTORY"
    medical_documents = "MEDICAL_DOCUMENTS"
    emergency_information = "EMERGENCY_INFORMATION"


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    display_name: str = Field(min_length=1, max_length=100)
    profile: PatientCreate | None = None
    patient_id: int | None = Field(default=None, ge=1)

    @field_validator("display_name", mode="before")
    @classmethod
    def strip_display_name(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @model_validator(mode="after")
    def require_one_profile_source(self) -> "UserCreate":
        if (self.profile is None) == (self.patient_id is None):
            raise ValueError("Provide exactly one of profile or patient_id")
        return self


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    email: EmailStr
    display_name: str
    patient_id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool


class FamilyGroupCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=100)

    @field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class FamilyGroupUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=100)
    is_active: bool | None = None

    @field_validator("name", mode="before")
    @classmethod
    def strip_name(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @model_validator(mode="after")
    def require_change(self) -> "FamilyGroupUpdate":
        if self.name is None and self.is_active is None:
            raise ValueError("Provide name or is_active")
        return self


class FamilyGroupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    family_group_id: int
    name: str
    created_by_user_id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool


class MembershipCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: int = Field(ge=1)
    role: FamilyRole = FamilyRole.member
    relationship: FamilyRelationship = FamilyRelationship.other

    @field_validator("role", mode="before")
    @classmethod
    def validate_role(cls, value: object) -> FamilyRole:
        try:
            return FamilyRole(value)
        except (TypeError, ValueError) as error:
            raise PydanticCustomError(
                "INVALID_FAMILY_ROLE",
                "Role must be OWNER, ADMIN, or MEMBER",
            ) from error

    @field_validator("relationship", mode="before")
    @classmethod
    def validate_relationship(cls, value: object) -> FamilyRelationship:
        try:
            return FamilyRelationship(value)
        except (TypeError, ValueError) as error:
            raise PydanticCustomError(
                "INVALID_FAMILY_RELATIONSHIP",
                "Unsupported family relationship",
            ) from error


class MembershipUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: FamilyRole | None = None
    relationship: FamilyRelationship | None = None
    status: MembershipStatus | None = None

    @field_validator("role", mode="before")
    @classmethod
    def validate_role(cls, value: object) -> FamilyRole | None:
        if value is None:
            return None
        try:
            return FamilyRole(value)
        except (TypeError, ValueError) as error:
            raise PydanticCustomError(
                "INVALID_FAMILY_ROLE",
                "Role must be OWNER, ADMIN, or MEMBER",
            ) from error

    @field_validator("relationship", mode="before")
    @classmethod
    def validate_relationship(cls, value: object) -> FamilyRelationship | None:
        if value is None:
            return None
        try:
            return FamilyRelationship(value)
        except (TypeError, ValueError) as error:
            raise PydanticCustomError(
                "INVALID_FAMILY_RELATIONSHIP",
                "Unsupported family relationship",
            ) from error

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, value: object) -> MembershipStatus | None:
        if value is None:
            return None
        try:
            return MembershipStatus(value)
        except (TypeError, ValueError) as error:
            raise PydanticCustomError(
                "INVALID_MEMBERSHIP_STATUS",
                "Unsupported membership status",
            ) from error

    @model_validator(mode="after")
    def require_change(self) -> "MembershipUpdate":
        if self.role is None and self.relationship is None and self.status is None:
            raise ValueError("Provide role, relationship, or status")
        return self


class MembershipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    membership_id: int
    family_group_id: int
    user_id: int
    role: FamilyRole
    relationship: FamilyRelationship = Field(validation_alias="relationship_type")
    status: MembershipStatus
    joined_at: datetime | None
    left_at: datetime | None
    created_at: datetime
    updated_at: datetime


class UserFamilyGroupResponse(BaseModel):
    family_group: FamilyGroupResponse
    membership: MembershipResponse


class PermissionValue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    data_type: FamilyDataType
    can_view: bool
    can_edit: bool

    @field_validator("data_type", mode="before")
    @classmethod
    def validate_data_type(cls, value: object) -> FamilyDataType:
        try:
            return FamilyDataType(value)
        except (TypeError, ValueError) as error:
            raise PydanticCustomError(
                "INVALID_PERMISSION_TYPE",
                "Unsupported family permission data type",
            ) from error


class PermissionUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    permissions: list[PermissionValue] = Field(min_length=1)

    @model_validator(mode="after")
    def reject_duplicate_types(self) -> "PermissionUpdate":
        types = [permission.data_type for permission in self.permissions]
        if len(types) != len(set(types)):
            raise ValueError("Permission data types must not be duplicated")
        return self


class PermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    permission_id: int
    membership_id: int
    data_type: FamilyDataType
    can_view: bool
    can_edit: bool
    created_at: datetime
    updated_at: datetime
