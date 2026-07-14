"""Add development accounts, family groups, memberships, and permissions."""

from alembic import op
import sqlalchemy as sa

revision = "0002_accounts_and_families"
down_revision = "0001_phase3_baseline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_accounts",
        sa.Column("user_id", sa.Integer(), primary_key=True),
        sa.Column(
            "email",
            sa.String(254),
            nullable=False,
            unique=True,
        ),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column(
            "patient_id",
            sa.Integer(),
            sa.ForeignKey("patients.id", ondelete="RESTRICT"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )

    op.create_table(
        "family_groups",
        sa.Column("family_group_id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column(
            "created_by_user_id",
            sa.Integer(),
            sa.ForeignKey("user_accounts.user_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )
    op.create_index(
        "ix_family_groups_created_by_user_id",
        "family_groups",
        ["created_by_user_id"],
    )

    op.create_table(
        "family_memberships",
        sa.Column("membership_id", sa.Integer(), primary_key=True),
        sa.Column(
            "family_group_id",
            sa.Integer(),
            sa.ForeignKey("family_groups.family_group_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("user_accounts.user_id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("relationship", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("left_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.CheckConstraint(
            "role IN ('OWNER', 'ADMIN', 'MEMBER')",
            name="ck_family_membership_role",
        ),
        sa.CheckConstraint(
            "relationship IN ('SELF', 'SPOUSE', 'CHILD', 'PARENT', 'SIBLING', "
            "'RELATIVE', 'CAREGIVER', 'OTHER')",
            name="ck_family_membership_relationship",
        ),
        sa.CheckConstraint(
            "status IN ('PENDING', 'ACTIVE', 'LEFT', 'REMOVED', 'DECLINED')",
            name="ck_family_membership_status",
        ),
    )
    op.create_index(
        "ix_family_memberships_family_group_id",
        "family_memberships",
        ["family_group_id"],
    )
    op.create_index(
        "ix_family_memberships_user_id",
        "family_memberships",
        ["user_id"],
    )
    op.create_index(
        "uq_active_membership_user_group",
        "family_memberships",
        ["family_group_id", "user_id"],
        unique=True,
        sqlite_where=sa.text("status = 'ACTIVE'"),
        postgresql_where=sa.text("status = 'ACTIVE'"),
    )

    op.create_table(
        "family_data_permissions",
        sa.Column("permission_id", sa.Integer(), primary_key=True),
        sa.Column(
            "membership_id",
            sa.Integer(),
            sa.ForeignKey("family_memberships.membership_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("data_type", sa.String(30), nullable=False),
        sa.Column(
            "can_view",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "can_edit",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.current_timestamp(),
        ),
        sa.UniqueConstraint(
            "membership_id",
            "data_type",
            name="uq_membership_permission_type",
        ),
        sa.CheckConstraint(
            "data_type IN ('BASIC_PROFILE', 'ALLERGIES', 'CURRENT_MEDICATIONS', "
            "'SCREENING_HISTORY', 'MEDICAL_DOCUMENTS', 'EMERGENCY_INFORMATION')",
            name="ck_family_permission_data_type",
        ),
    )
    op.create_index(
        "ix_family_data_permissions_membership_id",
        "family_data_permissions",
        ["membership_id"],
    )


def downgrade() -> None:
    op.drop_table("family_data_permissions")
    op.drop_table("family_memberships")
    op.drop_table("family_groups")
    op.drop_table("user_accounts")
