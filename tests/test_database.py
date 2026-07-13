from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import Connection, create_engine, inspect, text

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
            "alembic_version",
        } <= tables


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
        unique_indexes = [
            index
            for index in inspect(connection).get_indexes("allergies")
            if index.get("unique")
        ]
        patient_count = connection.scalar(text("SELECT COUNT(*) FROM patients"))
        allergy_count = connection.scalar(text("SELECT COUNT(*) FROM allergies"))
        assert "rxcui" in columns
        assert any(
            index["column_names"] == ["patient_id", "substance"]
            for index in unique_indexes
        )
        assert patient_count == 1
        assert allergy_count == 1
