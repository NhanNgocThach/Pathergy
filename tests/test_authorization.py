import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app import models, schemas
from app.main import app
from app.routes.medications import get_rxnorm_service
from tests.helpers import (
    add_and_activate_member,
    create_authenticated_user,
    create_group,
    set_permission,
)


class FakeRxNormService:
    def search_medication(self, drug_name: str) -> schemas.MedicationSearchResponse:
        return schemas.MedicationSearchResponse(
            query=drug_name,
            normalized_name="aspirin",
            rxcui="1191",
            active_ingredients=[
                schemas.MedicationIngredient(rxcui="1191", name="aspirin")
            ],
            ingredient_data_complete=True,
        )


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("get", "/patients"),
        ("get", "/patients/1/allergies"),
        ("post", "/patients/1/medication-check"),
        ("get", "/patients/1/screening-history"),
        ("get", "/family-groups/1"),
        ("get", "/users/1"),
    ],
)
def test_protected_apis_require_authentication(
    client: TestClient, method: str, path: str
) -> None:
    kwargs = {"json": {"medication_name": "Aspirin"}} if method == "post" else {}
    response = getattr(client, method)(path, **kwargs)
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "AUTHENTICATION_REQUIRED"


def test_invalid_access_token_is_rejected(client: TestClient) -> None:
    response = client.get(
        "/patients", headers={"Authorization": "Bearer invalid-token"}
    )
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "INVALID_ACCESS_TOKEN"


def test_openapi_marks_protected_and_public_routes(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()
    assert schema["paths"]["/patients"]["get"]["security"] == [
        {"HTTPBearer": []}
    ]
    assert schema["paths"]["/family-groups/{family_group_id}"]["get"][
        "security"
    ] == [{"HTTPBearer": []}]
    assert "security" not in schema["paths"]["/medications/search"]["get"]


def test_unrelated_user_cannot_access_health_data_by_changing_ids(
    client: TestClient,
) -> None:
    owner = create_authenticated_user(client, "health.owner@example.com")
    outsider = create_authenticated_user(client, "health.outsider@example.com")
    patient_id = owner["patient_id"]

    profile = client.get(f"/patients/{patient_id}", headers=outsider["headers"])
    allergies = client.get(
        f"/patients/{patient_id}/allergies", headers=outsider["headers"]
    )
    medication_check = client.post(
        f"/patients/{patient_id}/medication-check",
        json={"medication_name": "Aspirin"},
        headers=outsider["headers"],
    )

    for response in (profile, allergies, medication_check):
        assert response.status_code == 404
        assert response.json()["detail"]["code"] == "PATIENT_ACCESS_DENIED"


def test_basic_profile_view_and_edit_are_enforced_separately(
    client: TestClient,
) -> None:
    requester = create_authenticated_user(client, "profile.requester@example.com")
    target = create_authenticated_user(client, "profile.target@example.com")
    group = create_group(client, requester)
    add_and_activate_member(client, group, requester, target)
    set_permission(
        client, group, target, "BASIC_PROFILE", can_view=True, can_edit=False
    )

    viewed = client.get(
        f"/patients/{target['patient_id']}", headers=requester["headers"]
    )
    edited = client.put(
        f"/patients/{target['patient_id']}",
        json={
            "first_name": "Changed",
            "last_name": "Person",
            "date_of_birth": "1990-01-01",
        },
        headers=requester["headers"],
    )

    assert viewed.status_code == 200
    assert edited.status_code == 403
    assert edited.json()["detail"]["code"] == "FAMILY_PERMISSION_DENIED"


def test_allergy_view_and_edit_are_enforced_separately(client: TestClient) -> None:
    requester = create_authenticated_user(client, "allergy.requester@example.com")
    target = create_authenticated_user(client, "allergy.target@example.com")
    group = create_group(client, requester)
    add_and_activate_member(client, group, requester, target)
    target_path = f"/patients/{target['patient_id']}/allergies"
    client.post(
        target_path,
        json={
            "substance": "Aspirin",
            "reaction": "Fictional reaction",
            "severity": "mild",
        },
        headers=target["headers"],
    )
    set_permission(client, group, target, "ALLERGIES", can_view=True, can_edit=False)

    viewed = client.get(target_path, headers=requester["headers"])
    edited = client.post(
        target_path,
        json={
            "substance": "Latex",
            "reaction": "Fictional reaction",
            "severity": "mild",
        },
        headers=requester["headers"],
    )

    assert viewed.status_code == 200
    assert len(viewed.json()) == 1
    assert edited.status_code == 403


def test_owner_role_does_not_bypass_target_health_permissions(
    client: TestClient,
) -> None:
    owner = create_authenticated_user(client, "rolehealth.owner@example.com")
    member = create_authenticated_user(client, "rolehealth.member@example.com")
    group = create_group(client, owner)
    add_and_activate_member(client, group, owner, member)

    response = client.get(
        f"/patients/{member['patient_id']}/allergies", headers=owner["headers"]
    )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "FAMILY_PERMISSION_DENIED"


def test_family_medication_check_requires_both_permissions_and_stores_history(
    client: TestClient,
    session_factory: sessionmaker[Session],
) -> None:
    requester = create_authenticated_user(client, "check.requester@example.com")
    target = create_authenticated_user(client, "check.target@example.com")
    group = create_group(client, requester)
    add_and_activate_member(client, group, requester, target)
    set_permission(client, group, target, "ALLERGIES", can_view=True, can_edit=False)
    app.dependency_overrides[get_rxnorm_service] = FakeRxNormService
    path = f"/patients/{target['patient_id']}/medication-check"

    denied = client.post(
        path,
        json={"medication_name": "Aspirin"},
        headers=requester["headers"],
    )
    with session_factory() as db:
        assert list(db.scalars(select(models.SearchHistory))) == []

    set_permission(
        client,
        group,
        target,
        "SCREENING_HISTORY",
        can_view=False,
        can_edit=True,
    )
    allowed = client.post(
        path,
        json={"medication_name": "Aspirin"},
        headers=requester["headers"],
    )

    assert denied.status_code == 403
    assert allowed.status_code == 200
    with session_factory() as db:
        assert len(list(db.scalars(select(models.SearchHistory)))) == 1


def test_screening_history_requires_view_permission(client: TestClient) -> None:
    requester = create_authenticated_user(client, "history.requester@example.com")
    target = create_authenticated_user(client, "history.target@example.com")
    group = create_group(client, requester)
    add_and_activate_member(client, group, requester, target)
    path = f"/patients/{target['patient_id']}/screening-history"

    denied = client.get(path, headers=requester["headers"])
    set_permission(
        client,
        group,
        target,
        "SCREENING_HISTORY",
        can_view=True,
        can_edit=False,
    )
    allowed = client.get(path, headers=requester["headers"])

    assert denied.status_code == 403
    assert allowed.status_code == 200
