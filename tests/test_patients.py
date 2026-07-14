from fastapi.testclient import TestClient

from tests.helpers import create_authenticated_user


def test_user_can_list_get_and_update_own_patient(client: TestClient) -> None:
    user = create_authenticated_user(client, "patient.owner@example.com")
    patient_id = user["patient_id"]

    listed = client.get("/patients", headers=user["headers"])
    retrieved = client.get(f"/patients/{patient_id}", headers=user["headers"])
    updated = client.put(
        f"/patients/{patient_id}",
        json={
            "first_name": "Updated",
            "last_name": "Person",
            "date_of_birth": "1990-01-01",
        },
        headers=user["headers"],
    )

    assert listed.status_code == 200
    assert [patient["id"] for patient in listed.json()] == [patient_id]
    assert retrieved.status_code == 200
    assert updated.status_code == 200
    assert updated.json()["first_name"] == "Updated"


def test_personal_profile_cannot_be_deleted(client: TestClient) -> None:
    user = create_authenticated_user(client, "patient.delete@example.com")

    response = client.delete(
        f"/patients/{user['patient_id']}", headers=user["headers"]
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "PERSONAL_PROFILE_DELETE_FORBIDDEN"


def test_patient_validation_and_missing_patient(client: TestClient) -> None:
    user = create_authenticated_user(client, "patient.validation@example.com")
    invalid = client.put(
        f"/patients/{user['patient_id']}",
        json={
            "first_name": "   ",
            "last_name": "Person",
            "date_of_birth": "2999-01-01",
        },
        headers=user["headers"],
    )
    missing = client.get("/patients/999", headers=user["headers"])

    assert invalid.status_code == 422
    assert missing.status_code == 404
    assert missing.json()["detail"]["code"] == "PATIENT_NOT_FOUND"
    assert client.get("/patients/0", headers=user["headers"]).status_code == 422


def test_swagger_documentation_is_available(client: TestClient) -> None:
    response = client.get("/docs")
    assert response.status_code == 200
    assert "swagger-ui" in response.text.lower()
