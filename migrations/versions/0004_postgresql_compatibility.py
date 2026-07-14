"""Add the portable case-insensitive allergy uniqueness index."""

from alembic import op
import sqlalchemy as sa

revision = "0004_postgresql_compatibility"
down_revision = "0003_authentication"
branch_labels = None
depends_on = None


def index_names(table_name: str) -> set[str]:
    if op.get_bind().dialect.name == "sqlite":
        return set(
            op.get_bind()
            .execute(
                sa.text(
                    "SELECT name FROM sqlite_master "
                    "WHERE type = 'index' AND tbl_name = :table_name"
                ),
                {"table_name": table_name},
            )
            .scalars()
        )
    return {
        index["name"]
        for index in sa.inspect(op.get_bind()).get_indexes(table_name)
        if index["name"] is not None
    }


def upgrade() -> None:
    if "uq_allergy_patient_substance_ci" not in index_names("allergies"):
        op.create_index(
            "uq_allergy_patient_substance_ci",
            "allergies",
            ["patient_id", sa.text("lower(substance)")],
            unique=True,
        )


def downgrade() -> None:
    if "uq_allergy_patient_substance_ci" in index_names("allergies"):
        op.drop_index("uq_allergy_patient_substance_ci", table_name="allergies")
