"""Establish the existing Phase 3 schema without replacing existing tables."""

from alembic import op
import sqlalchemy as sa

revision = "0001_phase3_baseline"
down_revision = None
branch_labels = None
depends_on = None


def table_names() -> set[str]:
    return set(sa.inspect(op.get_bind()).get_table_names())


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
    tables = table_names()

    if "patients" not in tables:
        op.create_table(
            "patients",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("first_name", sa.String(50), nullable=False),
            sa.Column("last_name", sa.String(50), nullable=False),
            sa.Column("date_of_birth", sa.Date(), nullable=False),
        )

    if "allergies" not in tables:
        op.create_table(
            "allergies",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "patient_id",
                sa.Integer(),
                sa.ForeignKey("patients.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("substance", sa.String(100), nullable=False),
            sa.Column("rxcui", sa.String(20), nullable=True),
            sa.Column("reaction", sa.String(200), nullable=True),
            sa.Column("severity", sa.String(20), nullable=False),
        )
    else:
        allergy_columns = {
            column["name"]
            for column in sa.inspect(op.get_bind()).get_columns("allergies")
        }
        if "rxcui" not in allergy_columns:
            op.add_column("allergies", sa.Column("rxcui", sa.String(20)))

    if "ix_allergies_patient_id" not in index_names("allergies"):
        op.create_index("ix_allergies_patient_id", "allergies", ["patient_id"])

    if "uq_allergy_patient_substance_ci" not in index_names("allergies"):
        op.create_index(
            "uq_allergy_patient_substance_ci",
            "allergies",
            ["patient_id", sa.text("lower(substance)")],
            unique=True,
        )

    if "search_history" not in table_names():
        op.create_table(
            "search_history",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "patient_id",
                sa.Integer(),
                sa.ForeignKey("patients.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("medication_name", sa.String(100), nullable=False),
            sa.Column("normalized_medication_name", sa.String(300), nullable=True),
            sa.Column("medication_rxcui", sa.String(20), nullable=True),
            sa.Column("result", sa.String(40), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                nullable=False,
                server_default=sa.func.current_timestamp(),
            ),
        )
    if "ix_search_history_patient_id" not in index_names("search_history"):
        op.create_index(
            "ix_search_history_patient_id",
            "search_history",
            ["patient_id"],
        )


def downgrade() -> None:
    tables = table_names()
    if "search_history" in tables:
        op.drop_table("search_history")
    if "allergies" in tables:
        op.drop_table("allergies")
    if "patients" in tables:
        op.drop_table("patients")
