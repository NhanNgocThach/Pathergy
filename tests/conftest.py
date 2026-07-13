from collections.abc import Generator
import os

os.environ["AUTH_JWT_SECRET"] = "test-jwt-secret-that-is-at-least-32-characters"
os.environ["AUTH_TOKEN_HASH_SECRET"] = (
    "test-token-hash-secret-that-is-at-least-32-characters"
)
os.environ["AUTH_DEVELOPMENT_MODE"] = "true"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.services.auth_security import auth_rate_limiter


@pytest.fixture()
def session_factory() -> Generator[sessionmaker[Session], None, None]:
    """Give each test a clean in-memory SQLite session factory."""
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(test_engine, "connect")
    def enable_foreign_keys(dbapi_connection, connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    testing_session_local = sessionmaker(
        bind=test_engine,
        autoflush=False,
        expire_on_commit=False,
    )
    Base.metadata.create_all(bind=test_engine)

    yield testing_session_local

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def client(
    session_factory: sessionmaker[Session],
) -> Generator[TestClient, None, None]:
    """Provide an API client connected to the isolated test database."""

    def override_get_db() -> Generator[Session, None, None]:
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    auth_rate_limiter.clear()
    app.dependency_overrides[get_db] = override_get_db
    # Avoid entering the app lifespan here: it creates production tables using
    # app.database.engine. The test tables above are already ready to use.
    test_client = TestClient(app)
    yield test_client
    test_client.close()
    app.dependency_overrides.clear()
    auth_rate_limiter.clear()
