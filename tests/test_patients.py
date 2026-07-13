from fastapi.testclient import TestClient


FICTIONAL_PATIENT = {
    "first_name": "Jamie",
    "last_name": "Rivera",
    "date_of_birth": "1994-06-15",
}


def test_patient_crud(client: TestClient) -> None:
    create_response = client.post("/patients", json=FICTIONAL_PATIENT)
    assert create_response.status_code == 201
    patient_id = create_response.json()["id"]

    list_response = client.get("/patients")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    get_response = client.get(f"/patients/{patient_id}")
    assert get_response.status_code == 200
    assert get_response.json()["first_name"] == "Jamie"

    updated_patient = {
        "first_name": "Jordan",
        "last_name": "Rivera",
        "date_of_birth": "1994-06-15",
    }
    update_response = client.put(f"/patients/{patient_id}", json=updated_patient)
    assert update_response.status_code == 200
    assert update_response.json()["first_name"] == "Jordan"

    delete_response = client.delete(f"/patients/{patient_id}")
    assert delete_response.status_code == 204
    assert client.get(f"/patients/{patient_id}").status_code == 404


def test_patient_validation_rejects_future_birth_date(client: TestClient) -> None:
    invalid_patient = {
        **FICTIONAL_PATIENT,
        "date_of_birth": "2999-01-01",
    }

    response = client.post("/patients", json=invalid_patient)

    assert response.status_code == 422


def test_missing_patient_returns_clear_error(client: TestClient) -> None:
    response = client.get("/patients/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Patient not found"}


def test_patient_rejects_blank_names_extra_fields_and_invalid_id(
    client: TestClient,
) -> None:
    blank_name_response = client.post(
        "/patients",
        json={**FICTIONAL_PATIENT, "first_name": "   "},
    )
    assert blank_name_response.status_code == 422

    extra_field_response = client.post(
        "/patients",
        json={**FICTIONAL_PATIENT, "medical_record_number": "NOT-ALLOWED"},
    )
    assert extra_field_response.status_code == 422

    assert client.get("/patients/0").status_code == 422


def test_swagger_documentation_is_available(client: TestClient) -> None:
    response = client.get("/docs")

    assert response.status_code == 200
    assert "swagger-ui" in response.text.lower()
