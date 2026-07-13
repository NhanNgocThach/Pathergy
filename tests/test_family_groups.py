from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app import models, schemas


def create_user(client: TestClient, number: int) -> dict:
    response = client.post(
        "/users",
        json={
            "email": f"fictional.family{number}@example.com",
            "display_name": f"Fictional Family Person {number}",
            "profile": {
                "first_name": f"Person{number}",
                "last_name": "Fictional",
                "date_of_birth": "1990-01-01",
            },
        },
    )
    assert response.status_code == 201
    return response.json()


def create_group(client: TestClient, owner_id: int, name: str) -> dict:
    response = client.post(
        "/family-groups",
        json={"requesting_user_id": owner_id, "name": name},
    )
    assert response.status_code == 201
    return response.json()


def add_member(client: TestClient, group_id: int, owner_id: int, user_id: int):
    return client.post(
        f"/family-groups/{group_id}/members",
        json={
            "requesting_user_id": owner_id,
            "user_id": user_id,
            "role": "MEMBER",
            "relationship": "RELATIVE",
        },
    )


def activate_member(client: TestClient, group_id: int, owner_id: int, user_id: int):
    return client.put(
        f"/family-groups/{group_id}/members/{user_id}",
        json={"requesting_user_id": owner_id, "status": "ACTIVE"},
    )


def test_create_group_creator_is_owner_and_group_is_retrievable(
    client: TestClient,
) -> None:
    owner = create_user(client, 1)
    group = create_group(client, owner["user_id"], "Fictional Household A")

    get_response = client.get(
        f"/family-groups/{group['family_group_id']}",
        params={"requesting_user_id": owner["user_id"]},
    )
    members = client.get(
        f"/family-groups/{group['family_group_id']}/members",
        params={"requesting_user_id": owner["user_id"]},
    ).json()
    listed_groups = client.get(
        f"/users/{owner['user_id']}/family-groups",
        params={"requesting_user_id": owner["user_id"]},
    ).json()

    assert get_response.status_code == 200
    assert members[0]["role"] == "OWNER"
    assert members[0]["status"] == "ACTIVE"
    assert members[0]["relationship"] == "SELF"
    assert listed_groups[0]["family_group"]["family_group_id"] == group["family_group_id"]


def test_member_joins_multiple_groups_and_duplicate_active_is_rejected(
    client: TestClient,
) -> None:
    owner = create_user(client, 1)
    member = create_user(client, 2)
    group_a = create_group(client, owner["user_id"], "Fictional Group A")
    group_b = create_group(client, owner["user_id"], "Fictional Group B")

    for group in (group_a, group_b):
        pending = add_member(
            client,
            group["family_group_id"],
            owner["user_id"],
            member["user_id"],
        )
        assert pending.status_code == 201
        assert pending.json()["status"] == "PENDING"
        activated = activate_member(
            client,
            group["family_group_id"],
            owner["user_id"],
            member["user_id"],
        )
        assert activated.status_code == 200

    groups = client.get(
        f"/users/{member['user_id']}/family-groups",
        params={"requesting_user_id": member["user_id"]},
    ).json()
    duplicate = add_member(
        client,
        group_a["family_group_id"],
        owner["user_id"],
        member["user_id"],
    )

    assert len(groups) == 2
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"]["code"] == "DUPLICATE_ACTIVE_MEMBERSHIP"


def test_update_member_role_relationship_and_list_members(client: TestClient) -> None:
    owner = create_user(client, 1)
    member = create_user(client, 2)
    group = create_group(client, owner["user_id"], "Fictional Household")
    add_member(client, group["family_group_id"], owner["user_id"], member["user_id"])
    activate_member(client, group["family_group_id"], owner["user_id"], member["user_id"])

    update = client.put(
        f"/family-groups/{group['family_group_id']}/members/{member['user_id']}",
        json={
            "requesting_user_id": owner["user_id"],
            "role": "ADMIN",
            "relationship": "CAREGIVER",
        },
    )
    members = client.get(
        f"/family-groups/{group['family_group_id']}/members",
        params={"requesting_user_id": member["user_id"]},
    )

    assert update.status_code == 200
    assert update.json()["role"] == "ADMIN"
    assert update.json()["relationship"] == "CAREGIVER"
    assert len(members.json()) == 2


def test_pending_and_outside_users_have_no_group_access(client: TestClient) -> None:
    owner = create_user(client, 1)
    pending_user = create_user(client, 2)
    outsider = create_user(client, 3)
    group = create_group(client, owner["user_id"], "Fictional Household")
    add_member(
        client,
        group["family_group_id"],
        owner["user_id"],
        pending_user["user_id"],
    )

    for user in (pending_user, outsider):
        response = client.get(
            f"/family-groups/{group['family_group_id']}",
            params={"requesting_user_id": user["user_id"]},
        )
        assert response.status_code == 403
        assert response.json()["detail"]["code"] == "FAMILY_ACCESS_DENIED"


def test_member_leaves_without_losing_health_data(
    client: TestClient,
    session_factory: sessionmaker[Session],
) -> None:
    owner = create_user(client, 1)
    member = create_user(client, 2)
    group = create_group(client, owner["user_id"], "Fictional Household")
    add_member(client, group["family_group_id"], owner["user_id"], member["user_id"])
    activate_member(client, group["family_group_id"], owner["user_id"], member["user_id"])
    allergy = client.post(
        f"/patients/{member['patient_id']}/allergies",
        json={
            "substance": "Fictional allergen",
            "reaction": "Fictional reaction",
            "severity": "mild",
        },
    )
    assert allergy.status_code == 201
    with session_factory() as db:
        db.add(
            models.SearchHistory(
                patient_id=member["patient_id"],
                medication_name="Fictional medication",
                result=schemas.MedicationCheckResult.unable_to_verify.value,
            )
        )
        db.commit()

    leave = client.post(
        f"/family-groups/{group['family_group_id']}/members/{member['user_id']}/leave",
        json={"requesting_user_id": member["user_id"]},
    )

    assert leave.status_code == 200
    assert leave.json()["status"] == "LEFT"
    assert leave.json()["left_at"] is not None
    assert client.get(f"/users/{member['user_id']}/profile").status_code == 200
    assert len(client.get(f"/patients/{member['patient_id']}/allergies").json()) == 1
    with session_factory() as db:
        assert db.scalar(select(models.SearchHistory)) is not None
    denied = client.get(
        f"/family-groups/{group['family_group_id']}",
        params={"requesting_user_id": member["user_id"]},
    )
    assert denied.status_code == 403


def test_removed_member_loses_access_but_keeps_profile(client: TestClient) -> None:
    owner = create_user(client, 1)
    member = create_user(client, 2)
    group = create_group(client, owner["user_id"], "Fictional Household")
    add_member(client, group["family_group_id"], owner["user_id"], member["user_id"])
    activate_member(client, group["family_group_id"], owner["user_id"], member["user_id"])

    removed = client.delete(
        f"/family-groups/{group['family_group_id']}/members/{member['user_id']}",
        params={"requesting_user_id": owner["user_id"]},
    )

    assert removed.status_code == 200
    assert removed.json()["status"] == "REMOVED"
    assert client.get(f"/users/{member['user_id']}/profile").status_code == 200
    denied = client.get(
        f"/family-groups/{group['family_group_id']}",
        params={"requesting_user_id": member["user_id"]},
    )
    assert denied.status_code == 403


def test_final_owner_cannot_leave_or_be_removed(client: TestClient) -> None:
    owner = create_user(client, 1)
    group = create_group(client, owner["user_id"], "Fictional Household")

    leave = client.post(
        f"/family-groups/{group['family_group_id']}/members/{owner['user_id']}/leave",
        json={"requesting_user_id": owner["user_id"]},
    )
    remove = client.delete(
        f"/family-groups/{group['family_group_id']}/members/{owner['user_id']}",
        params={"requesting_user_id": owner["user_id"]},
    )

    assert leave.status_code == 409
    assert remove.status_code == 409
    assert leave.json()["detail"]["code"] == "LAST_OWNER_CANNOT_LEAVE"


def test_member_can_join_new_group_after_leaving(client: TestClient) -> None:
    owner = create_user(client, 1)
    member = create_user(client, 2)
    group_a = create_group(client, owner["user_id"], "Fictional Group A")
    group_b = create_group(client, owner["user_id"], "Fictional Group B")
    add_member(client, group_a["family_group_id"], owner["user_id"], member["user_id"])
    activate_member(client, group_a["family_group_id"], owner["user_id"], member["user_id"])
    client.post(
        f"/family-groups/{group_a['family_group_id']}/members/{member['user_id']}/leave",
        json={"requesting_user_id": member["user_id"]},
    )

    pending = add_member(
        client,
        group_b["family_group_id"],
        owner["user_id"],
        member["user_id"],
    )

    assert pending.status_code == 201
    assert pending.json()["status"] == "PENDING"


def test_invalid_family_enums_return_stable_error_codes(client: TestClient) -> None:
    owner = create_user(client, 1)
    member = create_user(client, 2)
    group = create_group(client, owner["user_id"], "Fictional Household")

    invalid_role = client.post(
        f"/family-groups/{group['family_group_id']}/members",
        json={
            "requesting_user_id": owner["user_id"],
            "user_id": member["user_id"],
            "role": "SUPERUSER",
            "relationship": "RELATIVE",
        },
    )
    invalid_relationship = client.post(
        f"/family-groups/{group['family_group_id']}/members",
        json={
            "requesting_user_id": owner["user_id"],
            "user_id": member["user_id"],
            "relationship": "UNKNOWN",
        },
    )
    add_member(client, group["family_group_id"], owner["user_id"], member["user_id"])
    invalid_status = client.put(
        f"/family-groups/{group['family_group_id']}/members/{member['user_id']}",
        json={"requesting_user_id": owner["user_id"], "status": "SUSPENDED"},
    )

    assert invalid_role.json()["detail"]["code"] == "INVALID_FAMILY_ROLE"
    assert invalid_relationship.json()["detail"]["code"] == (
        "INVALID_FAMILY_RELATIONSHIP"
    )
    assert invalid_status.json()["detail"]["code"] == "INVALID_MEMBERSHIP_STATUS"


def test_regular_member_cannot_add_or_remove_members(client: TestClient) -> None:
    owner = create_user(client, 1)
    member = create_user(client, 2)
    third_user = create_user(client, 3)
    group = create_group(client, owner["user_id"], "Fictional Household")
    add_member(client, group["family_group_id"], owner["user_id"], member["user_id"])
    activate_member(client, group["family_group_id"], owner["user_id"], member["user_id"])

    add_attempt = add_member(
        client,
        group["family_group_id"],
        member["user_id"],
        third_user["user_id"],
    )
    remove_attempt = client.delete(
        f"/family-groups/{group['family_group_id']}/members/{owner['user_id']}",
        params={"requesting_user_id": member["user_id"]},
    )

    assert add_attempt.status_code == 403
    assert remove_attempt.status_code == 403
    assert add_attempt.json()["detail"]["code"] == "FAMILY_ACCESS_DENIED"
