from fastapi.testclient import TestClient

from tests.helpers import add_and_activate_member, create_authenticated_user, create_group


def test_creator_is_owner_and_can_retrieve_group(client: TestClient) -> None:
    owner = create_authenticated_user(client, "family.owner@example.com")
    group = create_group(client, owner)

    retrieved = client.get(
        f"/family-groups/{group['family_group_id']}", headers=owner["headers"]
    )
    members = client.get(
        f"/family-groups/{group['family_group_id']}/members",
        headers=owner["headers"],
    )
    own_groups = client.get(
        f"/users/{owner['user_id']}/family-groups", headers=owner["headers"]
    )

    assert retrieved.status_code == 200
    assert members.json()[0]["role"] == "OWNER"
    assert members.json()[0]["status"] == "ACTIVE"
    assert len(own_groups.json()) == 1


def test_owner_and_admin_can_manage_members(client: TestClient) -> None:
    owner = create_authenticated_user(client, "manage.owner@example.com")
    admin = create_authenticated_user(client, "manage.admin@example.com")
    new_member = create_authenticated_user(client, "manage.member@example.com")
    group = create_group(client, owner)
    add_and_activate_member(client, group, owner, admin, role="ADMIN")

    added = client.post(
        f"/family-groups/{group['family_group_id']}/members",
        json={"user_id": new_member["user_id"], "relationship": "RELATIVE"},
        headers=admin["headers"],
    )
    activated = client.put(
        f"/family-groups/{group['family_group_id']}/members/{new_member['user_id']}",
        json={"status": "ACTIVE"},
        headers=owner["headers"],
    )

    assert added.status_code == 201
    assert activated.status_code == 200


def test_regular_member_cannot_manage_members(client: TestClient) -> None:
    owner = create_authenticated_user(client, "role.owner@example.com")
    member = create_authenticated_user(client, "role.member@example.com")
    outsider = create_authenticated_user(client, "role.outsider@example.com")
    group = create_group(client, owner)
    add_and_activate_member(client, group, owner, member)

    response = client.post(
        f"/family-groups/{group['family_group_id']}/members",
        json={"user_id": outsider["user_id"]},
        headers=member["headers"],
    )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "INSUFFICIENT_ROLE"


def test_outside_pending_and_left_users_have_no_group_access(
    client: TestClient,
) -> None:
    owner = create_authenticated_user(client, "status.owner@example.com")
    pending = create_authenticated_user(client, "status.pending@example.com")
    active = create_authenticated_user(client, "status.active@example.com")
    outsider = create_authenticated_user(client, "status.outside@example.com")
    group = create_group(client, owner)
    client.post(
        f"/family-groups/{group['family_group_id']}/members",
        json={"user_id": pending["user_id"]},
        headers=owner["headers"],
    )
    add_and_activate_member(client, group, owner, active)
    left = client.post(
        f"/family-groups/{group['family_group_id']}/members/{active['user_id']}/leave",
        headers=active["headers"],
    )
    assert left.status_code == 200
    assert left.json()["status"] == "LEFT"

    for user in (pending, active, outsider):
        denied = client.get(
            f"/family-groups/{group['family_group_id']}", headers=user["headers"]
        )
        assert denied.status_code == 403
        assert denied.json()["detail"]["code"] == "FAMILY_ACCESS_DENIED"


def test_final_owner_cannot_leave_or_be_removed(client: TestClient) -> None:
    owner = create_authenticated_user(client, "last.owner@example.com")
    group = create_group(client, owner)
    path = f"/family-groups/{group['family_group_id']}/members/{owner['user_id']}"

    leave = client.post(f"{path}/leave", headers=owner["headers"])
    remove = client.delete(path, headers=owner["headers"])

    assert leave.status_code == 409
    assert remove.status_code == 409
    assert leave.json()["detail"]["code"] == "LAST_OWNER_CANNOT_LEAVE"


def test_client_supplied_requester_id_is_rejected_not_trusted(
    client: TestClient,
) -> None:
    owner = create_authenticated_user(client, "impersonation.owner@example.com")
    outsider = create_authenticated_user(client, "impersonation.outside@example.com")
    group = create_group(client, owner)

    query_attempt = client.get(
        f"/family-groups/{group['family_group_id']}",
        params={"requesting_user_id": owner["user_id"]},
        headers=outsider["headers"],
    )
    body_attempt = client.put(
        f"/family-groups/{group['family_group_id']}",
        json={"name": "Stolen", "requesting_user_id": owner["user_id"]},
        headers=outsider["headers"],
    )

    assert query_attempt.status_code == 403
    assert body_attempt.status_code == 422


def test_invalid_family_values_have_stable_errors(client: TestClient) -> None:
    owner = create_authenticated_user(client, "enum.owner@example.com")
    member = create_authenticated_user(client, "enum.member@example.com")
    group = create_group(client, owner)
    response = client.post(
        f"/family-groups/{group['family_group_id']}/members",
        json={"user_id": member["user_id"], "role": "SUPERUSER"},
        headers=owner["headers"],
    )
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "INVALID_FAMILY_ROLE"
