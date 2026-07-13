from fastapi.testclient import TestClient


def create_fictional_patient(client: TestClient) -> int:
    response = client.post(
        "/patients",
        json={
            "first_name": "Taylor",
            "last_name": "Morgan",
            "date_of_birth": "1988-11-03",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_allergy_crud(client: TestClient) -> None:
    patient_id = create_fictional_patient(client)
    allergy_data = {
        "substance": "Penicillin",
        "reaction": "Fictional example: skin rash",
        "severity": "moderate",
    }

    create_response = client.post(
        f"/patients/{patient_id}/allergies",
        json=allergy_data,
    )
    assert create_response.status_code == 201
    allergy_id = create_response.json()["id"]

    list_response = client.get(f"/patients/{patient_id}/allergies")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    get_response = client.get(f"/patients/{patient_id}/allergies/{allergy_id}")
    assert get_response.status_code == 200
    assert get_response.json()["substance"] == "Penicillin"

    updated_allergy = {
        **allergy_data,
        "reaction": "Fictional example: hives",
        "severity": "severe",
    }
    update_response = client.put(
        f"/patients/{patient_id}/allergies/{allergy_id}",
        json=updated_allergy,
    )
    assert update_response.status_code == 200
    assert update_response.json()["severity"] == "severe"

    delete_response = client.delete(
        f"/patients/{patient_id}/allergies/{allergy_id}"
    )
    assert delete_response.status_code == 204
    missing_response = client.get(
        f"/patients/{patient_id}/allergies/{allergy_id}"
    )
    assert missing_response.status_code == 404
    assert missing_response.json() == {"detail": "Allergy record not found"}


def test_patient_can_have_multiple_allergies(client: TestClient) -> None:
    patient_id = create_fictional_patient(client)
    for substance in ("Penicillin", "Latex"):
        response = client.post(
            f"/patients/{patient_id}/allergies",
            json={
                "substance": substance,
                "reaction": "Fictional example reaction",
                "severity": "mild",
            },
        )
        assert response.status_code == 201

    response = client.get(f"/patients/{patient_id}/allergies")

    assert len(response.json()) == 2


def test_allergy_validation_and_missing_patient(client: TestClient) -> None:
    invalid_response = client.post(
        "/patients/999/allergies",
        json={"substance": "X", "reaction": "rash", "severity": "unknown"},
    )
    assert invalid_response.status_code == 422

    valid_but_missing_patient_response = client.post(
        "/patients/999/allergies",
        json={
            "substance": "Latex",
            "reaction": "Fictional example reaction",
            "severity": "mild",
        },
    )
    assert valid_but_missing_patient_response.status_code == 404
    assert valid_but_missing_patient_response.json() == {"detail": "Patient not found"}


def test_duplicate_allergy_is_rejected_case_insensitively(client: TestClient) -> None:
    patient_id = create_fictional_patient(client)
    allergy = {
        "substance": "Penicillin",
        "reaction": "Fictional example reaction",
        "severity": "mild",
    }
    assert client.post(
        f"/patients/{patient_id}/allergies",
        json=allergy,
    ).status_code == 201

    duplicate_response = client.post(
        f"/patients/{patient_id}/allergies",
        json={**allergy, "substance": "  penicillin  "},
    )

    assert duplicate_response.status_code == 409
    assert duplicate_response.json() == {
        "detail": "This patient already has an allergy record for that substance"
    }


def test_updating_to_duplicate_allergy_is_rejected(client: TestClient) -> None:
    patient_id = create_fictional_patient(client)
    allergy_ids = []
    for substance in ("Penicillin", "Latex"):
        response = client.post(
            f"/patients/{patient_id}/allergies",
            json={
                "substance": substance,
                "reaction": "Fictional example reaction",
                "severity": "mild",
            },
        )
        allergy_ids.append(response.json()["id"])

    response = client.put(
        f"/patients/{patient_id}/allergies/{allergy_ids[1]}",
        json={
            "substance": "PENICILLIN",
            "reaction": "Fictional example reaction",
            "severity": "moderate",
        },
    )

    assert response.status_code == 409
    unchanged = client.get(
        f"/patients/{patient_id}/allergies/{allergy_ids[1]}"
    )
    assert unchanged.json()["substance"] == "Latex"


def test_allergy_rejects_whitespace_and_patient_delete_removes_access(
    client: TestClient,
) -> None:
    patient_id = create_fictional_patient(client)
    invalid_response = client.post(
        f"/patients/{patient_id}/allergies",
        json={"substance": " X ", "reaction": "  ", "severity": "mild"},
    )
    assert invalid_response.status_code == 422

    create_response = client.post(
        f"/patients/{patient_id}/allergies",
        json={
            "substance": "Latex",
            "reaction": None,
            "severity": "mild",
        },
    )
    allergy_id = create_response.json()["id"]

    assert client.delete(f"/patients/{patient_id}").status_code == 204
    nested_response = client.get(
        f"/patients/{patient_id}/allergies/{allergy_id}"
    )
    assert nested_response.status_code == 404
    assert nested_response.json() == {"detail": "Patient not found"}


def test_allergy_is_scoped_to_its_patient(client: TestClient) -> None:
    first_patient_id = create_fictional_patient(client)
    second_patient_response = client.post(
        "/patients",
        json={
            "first_name": "Casey",
            "last_name": "Lee",
            "date_of_birth": "1990-02-10",
        },
    )
    second_patient_id = second_patient_response.json()["id"]
    allergy = {
        "substance": "Latex",
        "reaction": "Fictional example reaction",
        "severity": "mild",
    }
    first_allergy_response = client.post(
        f"/patients/{first_patient_id}/allergies",
        json=allergy,
    )
    allergy_id = first_allergy_response.json()["id"]

    wrong_patient_response = client.get(
        f"/patients/{second_patient_id}/allergies/{allergy_id}"
    )
    assert wrong_patient_response.status_code == 404
    assert wrong_patient_response.json() == {"detail": "Allergy record not found"}

    # The uniqueness rule is per patient, so another patient may record Latex.
    second_allergy_response = client.post(
        f"/patients/{second_patient_id}/allergies",
        json=allergy,
    )
    assert second_allergy_response.status_code == 201
