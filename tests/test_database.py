from pathlib import Path

from alembic import command
from alembic.config import Config
import pytest
from sqlalchemy import Connection, create_engine, inspect, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import IntegrityError
from sqlalchemy.schema import CreateIndex, CreateTable

from app import models
from app.database import engine_options, normalize_database_url

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_migrations(connection: Connection) -> None:
    config = Config(str(PROJECT_ROOT / "alembic.ini"))
    config.attributes["connection"] = connection
    command.upgrade(config, "head")


def test_migrations_create_fresh_database() -> None:
    engine = create_engine("sqlite://")
    with engine.connect() as connection:
        run_migrations(connection)

        tables = set(inspect(connection).get_table_names())
        assert {
            "patients",
            "allergies",
            "search_history",
            "user_accounts",
            "family_groups",
            "family_memberships",
            "family_data_permissions",
            "auth_sessions",
            "used_refresh_tokens",
            "email_verification_tokens",
            "password_reset_tokens",
            "alembic_version",
        } <= tables
        user_columns = {
            column["name"]: column
            for column in inspect(connection).get_columns("user_accounts")
        }
        user_constraints = {
            constraint["name"]
            for constraint in inspect(connection).get_unique_constraints(
                "user_accounts"
            )
        }
        assert user_columns["email"]["nullable"] is True
        assert "phone_number" in user_columns
        assert "phone_verified_at" in user_columns
        assert "uq_user_accounts_phone_number" in user_constraints


def test_migrations_preserve_existing_health_data() -> None:
    engine = create_engine("sqlite://")
    with engine.connect() as connection:
        connection.execute(
            text(
                "CREATE TABLE patients ("
                "id INTEGER PRIMARY KEY, first_name VARCHAR(50) NOT NULL, "
                "last_name VARCHAR(50) NOT NULL, date_of_birth DATE NOT NULL)"
            )
        )
        connection.execute(
            text(
                "CREATE TABLE allergies ("
                "id INTEGER PRIMARY KEY, patient_id INTEGER NOT NULL, "
                "substance VARCHAR(100) NOT NULL, reaction VARCHAR(200), "
                "severity VARCHAR(20) NOT NULL)"
            )
        )
        connection.execute(
            text(
                "INSERT INTO patients VALUES "
                "(1, 'Fictional', 'Person', '1990-01-01')"
            )
        )
        connection.execute(
            text(
                "INSERT INTO allergies VALUES "
                "(1, 1, 'Fictional substance', NULL, 'mild')"
            )
        )
        connection.commit()

        run_migrations(connection)

        columns = {
            column["name"]
            for column in inspect(connection).get_columns("allergies")
        }
        index_names = set(
            connection.execute(
                text(
                    "SELECT name FROM sqlite_master "
                    "WHERE type = 'index' AND tbl_name = 'allergies'"
                )
            ).scalars()
        )
        patient_count = connection.scalar(text("SELECT COUNT(*) FROM patients"))
        allergy_count = connection.scalar(text("SELECT COUNT(*) FROM allergies"))
        assert "rxcui" in columns
        assert "uq_allergy_patient_substance_ci" in index_names
        assert patient_count == 1
        assert allergy_count == 1

        with pytest.raises(IntegrityError):
            connection.execute(
                text(
                    "INSERT INTO allergies "
                    "(id, patient_id, substance, reaction, severity) "
                    "VALUES (2, 1, 'FICTIONAL SUBSTANCE', NULL, 'mild')"
                )
            )


def test_database_url_and_pool_settings_support_sqlite_and_neon() -> None:
    assert normalize_database_url("sqlite:///./pathergy.db") == (
        "sqlite:///./pathergy.db"
    )
    assert normalize_database_url("postgresql://user:secret@host/db?sslmode=require") == (
        "postgresql+psycopg://user:secret@host/db?sslmode=require"
    )
    assert engine_options("sqlite://")["connect_args"] == {
        "check_same_thread": False
    }
    assert engine_options("postgresql+psycopg://user:secret@host/db") == {
        "pool_pre_ping": True,
        "pool_size": 5,
        "max_overflow": 5,
        "pool_recycle": 300,
    }


def test_model_schema_compiles_for_postgresql_without_sqlite_collations() -> None:
    dialect = postgresql.dialect()
    table_sql = "\n".join(
        str(CreateTable(table).compile(dialect=dialect))
        for table in models.Base.metadata.sorted_tables
    )
    index_sql = "\n".join(
        str(CreateIndex(index).compile(dialect=dialect))
        for table in models.Base.metadata.sorted_tables
        for index in table.indexes
    )

    assert "NOCASE" not in table_sql
    assert "lower(substance)" in index_sql
    assert "WHERE status = 'ACTIVE'" in index_sql
