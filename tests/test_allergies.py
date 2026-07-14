from fastapi.testclient import TestClient

from tests.helpers import create_authenticated_user


def allergy_payload(substance: str = "Penicillin") -> dict:
    return {
        "substance": substance,
        "reaction": "Fictional example reaction",
        "severity": "moderate",
    }


def test_owner_can_crud_allergies(client: TestClient) -> None:
    user = create_authenticated_user(client, "allergy.crud@example.com")
    patient_id = user["patient_id"]
    headers = user["headers"]

    created = client.post(
        f"/patients/{patient_id}/allergies",
        json=allergy_payload(),
        headers=headers,
    )
    allergy_id = created.json()["id"]
    listed = client.get(f"/patients/{patient_id}/allergies", headers=headers)
    updated = client.put(
        f"/patients/{patient_id}/allergies/{allergy_id}",
        json={**allergy_payload(), "severity": "severe"},
        headers=headers,
    )
    deleted = client.delete(
        f"/patients/{patient_id}/allergies/{allergy_id}", headers=headers
    )

    assert created.status_code == 201
    assert len(listed.json()) == 1
    assert updated.json()["severity"] == "severe"
    assert deleted.status_code == 204


def test_patient_can_have_multiple_allergies_and_reject_duplicates(
    client: TestClient,
) -> None:
    user = create_authenticated_user(client, "allergy.multiple@example.com")
    path = f"/patients/{user['patient_id']}/allergies"
    for substance in ("Penicillin", "Latex"):
        assert client.post(
            path, json=allergy_payload(substance), headers=user["headers"]
        ).status_code == 201

    duplicate = client.post(
        path,
        json=allergy_payload("  penicillin  "),
        headers=user["headers"],
    )
    assert len(client.get(path, headers=user["headers"]).json()) == 2
    assert duplicate.status_code == 409


def test_allergy_validation_and_nested_lookup(client: TestClient) -> None:
    first = create_authenticated_user(client, "allergy.first@example.com")
    invalid = client.post(
        f"/patients/{first['patient_id']}/allergies",
        json={"substance": "X", "reaction": " ", "severity": "unknown"},
        headers=first["headers"],
    )
    missing = client.get(
        f"/patients/{first['patient_id']}/allergies/999",
        headers=first["headers"],
    )

    assert invalid.status_code == 422
    assert missing.status_code == 404
    assert missing.json() == {"detail": "Allergy record not found"}
