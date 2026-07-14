from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app import models
from tests.helpers import create_authenticated_user


def test_authenticated_user_can_retrieve_own_account_and_profile(
    client: TestClient,
) -> None:
    user = create_authenticated_user(client, "account.owner@example.com")

    account = client.get(f"/users/{user['user_id']}", headers=user["headers"])
    profile = client.get(
        f"/users/{user['user_id']}/profile", headers=user["headers"]
    )

    assert account.status_code == 200
    assert account.json()["email"] == "account.owner@example.com"
    assert profile.status_code == 200
    assert profile.json()["id"] == user["patient_id"]


def test_user_cannot_retrieve_another_account(client: TestClient) -> None:
    first = create_authenticated_user(client, "account.first@example.com")
    second = create_authenticated_user(client, "account.second@example.com")

    response = client.get(
        f"/users/{second['user_id']}", headers=first["headers"]
    )

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "USER_ACCESS_DENIED"


def test_development_account_creation_requires_authentication(
    client: TestClient,
    session_factory: sessionmaker[Session],
) -> None:
    payload = {
        "email": "development.fixture@example.com",
        "display_name": "Development Fixture",
        "profile": {
            "first_name": "Development",
            "last_name": "Fixture",
            "date_of_birth": "1990-01-01",
        },
    }
    denied = client.post("/users", json=payload)
    actor = create_authenticated_user(client, "development.actor@example.com")
    created = client.post("/users", json=payload, headers=actor["headers"])

    assert denied.status_code == 401
    assert created.status_code == 201
    with session_factory() as db:
        fixture = db.scalar(
            select(models.UserAccount).where(
                models.UserAccount.email == "development.fixture@example.com"
            )
        )
        assert fixture is not None
        assert fixture.password_hash is None


def test_user_owned_profile_cannot_be_deleted_through_patient_crud(
    client: TestClient,
) -> None:
    user = create_authenticated_user(client, "account.delete@example.com")
    response = client.delete(
        f"/patients/{user['patient_id']}", headers=user["headers"]
    )
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "PERSONAL_PROFILE_DELETE_FORBIDDEN"
