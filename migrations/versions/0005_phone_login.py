"""Add optional Vietnamese phone login identifiers."""

from alembic import op
import sqlalchemy as sa

revision = "0005_phone_login"
down_revision = "0004_postgresql_compatibility"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("user_accounts") as batch_op:
        batch_op.alter_column(
            "email",
            existing_type=sa.String(254),
            nullable=True,
        )
        batch_op.add_column(
            sa.Column("phone_number", sa.String(16), nullable=True)
        )
        batch_op.add_column(
            sa.Column(
                "phone_verified_at",
                sa.DateTime(timezone=True),
                nullable=True,
            )
        )
        batch_op.create_unique_constraint(
            "uq_user_accounts_phone_number",
            ["phone_number"],
        )
        batch_op.create_check_constraint(
            "ck_user_account_login_identifier",
            "email IS NOT NULL OR phone_number IS NOT NULL",
        )


def downgrade() -> None:
    with op.batch_alter_table("user_accounts") as batch_op:
        batch_op.drop_constraint(
            "ck_user_account_login_identifier",
            type_="check",
        )
        batch_op.drop_constraint(
            "uq_user_accounts_phone_number",
            type_="unique",
        )
        batch_op.drop_column("phone_verified_at")
        batch_op.drop_column("phone_number")
        batch_op.alter_column(
            "email",
            existing_type=sa.String(254),
            nullable=False,
        )
