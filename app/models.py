from datetime import date, datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    date_of_birth: Mapped[date] = mapped_column(Date)

    allergies: Mapped[list["Allergy"]] = relationship(
        back_populates="patient",
        cascade="all, delete-orphan",
    )
    search_history: Mapped[list["SearchHistory"]] = relationship(
        back_populates="patient",
        cascade="all, delete-orphan",
    )
    user_account: Mapped["UserAccount | None"] = relationship(
        back_populates="profile",
        uselist=False,
    )


class Allergy(Base):
    __tablename__ = "allergies"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"),
        index=True,
    )
    substance: Mapped[str] = mapped_column(String(100))
    rxcui: Mapped[str | None] = mapped_column(String(20), nullable=True)
    reaction: Mapped[str | None] = mapped_column(String(200), nullable=True)
    severity: Mapped[str] = mapped_column(String(20))

    __table_args__ = (
        Index(
            "uq_allergy_patient_substance_ci",
            patient_id,
            func.lower(substance),
            unique=True,
        ),
    )

    patient: Mapped[Patient] = relationship(back_populates="allergies")


class SearchHistory(Base):
    __tablename__ = "search_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"),
        index=True,
    )
    medication_name: Mapped[str] = mapped_column(String(100))
    normalized_medication_name: Mapped[str | None] = mapped_column(
        String(300),
        nullable=True,
    )
    medication_rxcui: Mapped[str | None] = mapped_column(String(20), nullable=True)
    result: Mapped[str] = mapped_column(String(40))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    patient: Mapped[Patient] = relationship(back_populates="search_history")


class UserAccount(Base):
    __tablename__ = "user_accounts"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True)
    display_name: Mapped[str] = mapped_column(String(100))
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id", ondelete="RESTRICT"),
        unique=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    profile: Mapped[Patient] = relationship(back_populates="user_account")
    memberships: Mapped[list["FamilyMembership"]] = relationship(
        back_populates="user",
    )
    created_family_groups: Mapped[list["FamilyGroup"]] = relationship(
        back_populates="creator",
        foreign_keys="FamilyGroup.created_by_user_id",
    )
    auth_sessions: Mapped[list["AuthSession"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    email_verification_tokens: Mapped[list["EmailVerificationToken"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    password_reset_tokens: Mapped[list["PasswordResetToken"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class FamilyGroup(Base):
    __tablename__ = "family_groups"

    family_group_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    created_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("user_accounts.user_id", ondelete="RESTRICT"),
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    creator: Mapped[UserAccount] = relationship(
        back_populates="created_family_groups",
        foreign_keys=[created_by_user_id],
    )
    memberships: Mapped[list["FamilyMembership"]] = relationship(
        back_populates="family_group",
    )


class FamilyMembership(Base):
    __tablename__ = "family_memberships"
    __table_args__ = (
        CheckConstraint(
            "role IN ('OWNER', 'ADMIN', 'MEMBER')",
            name="ck_family_membership_role",
        ),
        CheckConstraint(
            "relationship IN ('SELF', 'SPOUSE', 'CHILD', 'PARENT', 'SIBLING', "
            "'RELATIVE', 'CAREGIVER', 'OTHER')",
            name="ck_family_membership_relationship",
        ),
        CheckConstraint(
            "status IN ('PENDING', 'ACTIVE', 'LEFT', 'REMOVED', 'DECLINED')",
            name="ck_family_membership_status",
        ),
        Index(
            "uq_active_membership_user_group",
            "family_group_id",
            "user_id",
            unique=True,
            sqlite_where=text("status = 'ACTIVE'"),
            postgresql_where=text("status = 'ACTIVE'"),
        ),
    )

    membership_id: Mapped[int] = mapped_column(primary_key=True)
    family_group_id: Mapped[int] = mapped_column(
        ForeignKey("family_groups.family_group_id", ondelete="RESTRICT"),
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user_accounts.user_id", ondelete="RESTRICT"),
        index=True,
    )
    role: Mapped[str] = mapped_column(String(20))
    relationship_type: Mapped[str] = mapped_column("relationship", String(20))
    status: Mapped[str] = mapped_column(String(20))
    joined_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    left_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    family_group: Mapped[FamilyGroup] = relationship(back_populates="memberships")
    user: Mapped[UserAccount] = relationship(back_populates="memberships")
    permissions: Mapped[list["FamilyDataPermission"]] = relationship(
        back_populates="membership",
        cascade="all, delete-orphan",
    )


class FamilyDataPermission(Base):
    __tablename__ = "family_data_permissions"
    __table_args__ = (
        UniqueConstraint(
            "membership_id",
            "data_type",
            name="uq_membership_permission_type",
        ),
        CheckConstraint(
            "data_type IN ('BASIC_PROFILE', 'ALLERGIES', 'CURRENT_MEDICATIONS', "
            "'SCREENING_HISTORY', 'MEDICAL_DOCUMENTS', 'EMERGENCY_INFORMATION')",
            name="ck_family_permission_data_type",
        ),
    )

    permission_id: Mapped[int] = mapped_column(primary_key=True)
    membership_id: Mapped[int] = mapped_column(
        ForeignKey("family_memberships.membership_id", ondelete="CASCADE"),
        index=True,
    )
    data_type: Mapped[str] = mapped_column(String(30))
    can_view: Mapped[bool] = mapped_column(Boolean, default=False)
    can_edit: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    membership: Mapped[FamilyMembership] = relationship(back_populates="permissions")


class AuthSession(Base):
    __tablename__ = "auth_sessions"

    session_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user_accounts.user_id", ondelete="CASCADE"),
        index=True,
    )
    refresh_token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    device_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    device_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    last_used_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user: Mapped[UserAccount] = relationship(back_populates="auth_sessions")
    used_refresh_tokens: Mapped[list["UsedRefreshToken"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )


class UsedRefreshToken(Base):
    __tablename__ = "used_refresh_tokens"

    used_token_id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[str] = mapped_column(
        ForeignKey("auth_sessions.session_id", ondelete="CASCADE"),
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    used_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    session: Mapped[AuthSession] = relationship(back_populates="used_refresh_tokens")


class EmailVerificationToken(Base):
    __tablename__ = "email_verification_tokens"

    token_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user_accounts.user_id", ondelete="CASCADE"),
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user: Mapped[UserAccount] = relationship(back_populates="email_verification_tokens")


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    token_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user_accounts.user_id", ondelete="CASCADE"),
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    user: Mapped[UserAccount] = relationship(back_populates="password_reset_tokens")
