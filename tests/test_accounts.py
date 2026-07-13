from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app import models


def user_payload(email: str = "fictional.one@example.com") -> dict:
    return {
        "email": email,
        "display_name": "Fictional Person One",
        "profile": {
            "first_name": "Fictional",
            "last_name": "Person",
            "date_of_birth": "1990-01-01",
        },
    }


def test_create_user_and_personal_profile(client: TestClient) -> None:
    create_response = client.post("/users", json=user_payload())

    assert create_response.status_code == 201
    user = create_response.json()
    assert user["email"] == "fictional.one@example.com"
    assert user["patient_id"] > 0

    get_response = client.get(f"/users/{user['user_id']}")
    profile_response = client.get(f"/users/{user['user_id']}/profile")
    assert get_response.status_code == 200
    assert profile_response.status_code == 200
    assert profile_response.json()["id"] == user["patient_id"]
    assert profile_response.json()["first_name"] == "Fictional"


def test_user_validation_and_missing_user_error(client: TestClient) -> None:
    invalid_email = client.post(
        "/users",
        json={**user_payload(), "email": "not-an-email"},
    )
    blank_name = client.post(
        "/users",
        json={**user_payload(), "display_name": "   "},
    )
    missing = client.get("/users/999")

    assert invalid_email.status_code == 422
    assert blank_name.status_code == 422
    assert missing.status_code == 404
    assert missing.json() == {
        "detail": {"code": "USER_NOT_FOUND", "message": "User account not found"}
    }


def test_existing_patient_and_allergy_can_become_personal_profile(
    client: TestClient,
) -> None:
    patient = client.post(
        "/patients",
        json={
            "first_name": "Existing",
            "last_name": "Fictional",
            "date_of_birth": "1985-03-02",
        },
    ).json()
    allergy = client.post(
        f"/patients/{patient['id']}/allergies",
        json={
            "substance": "Fictional allergen",
            "reaction": "Fictional reaction",
            "severity": "mild",
        },
    )
    assert allergy.status_code == 201

    user_response = client.post(
        "/users",
        json={
            "email": "linked.profile@example.com",
            "display_name": "Linked Fictional Profile",
            "patient_id": patient["id"],
        },
    )

    assert user_response.status_code == 201
    profile = client.get(f"/users/{user_response.json()['user_id']}/profile").json()
    assert profile["id"] == patient["id"]
    allergies = client.get(f"/patients/{patient['id']}/allergies").json()
    assert len(allergies) == 1


def test_patient_profile_cannot_belong_to_two_users(client: TestClient) -> None:
    first_user = client.post("/users", json=user_payload()).json()

    response = client.post(
        "/users",
        json={
            "email": "fictional.two@example.com",
            "display_name": "Fictional Person Two",
            "patient_id": first_user["patient_id"],
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "USER_PROFILE_ALREADY_EXISTS"


def test_user_creation_is_one_account_and_one_profile(
    client: TestClient,
    session_factory: sessionmaker[Session],
) -> None:
    client.post("/users", json=user_payload())

    with session_factory() as db:
        assert len(list(db.scalars(select(models.UserAccount)))) == 1
        assert len(list(db.scalars(select(models.Patient)))) == 1


def test_user_owned_profile_cannot_be_deleted_through_patient_crud(
    client: TestClient,
) -> None:
    user = client.post("/users", json=user_payload()).json()

    response = client.delete(f"/patients/{user['patient_id']}")

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "PERSONAL_PROFILE_DELETE_FORBIDDEN"
    assert client.get(f"/users/{user['user_id']}/profile").status_code == 200
