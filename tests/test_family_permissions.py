from fastapi.testclient import TestClient

from tests.helpers import (
    add_and_activate_member,
    create_authenticated_user,
    create_group,
    set_permission,
)


def test_permissions_are_separate_for_each_membership(client: TestClient) -> None:
    owner = create_authenticated_user(client, "permission.owner@example.com")
    member = create_authenticated_user(client, "permission.member@example.com")
    group_a = create_group(client, owner, "Family A")
    group_b = create_group(client, owner, "Family B")
    add_and_activate_member(client, group_a, owner, member)
    add_and_activate_member(client, group_b, owner, member)

    assert set_permission(
        client, group_a, member, "ALLERGIES", can_view=True, can_edit=False
    ).status_code == 200
    permissions_b = client.get(
        f"/family-groups/{group_b['family_group_id']}/members/"
        f"{member['user_id']}/permissions",
        headers=member["headers"],
    ).json()

    values_b = {item["data_type"]: item["can_view"] for item in permissions_b}
    assert values_b["ALLERGIES"] is False


def test_owner_has_no_automatic_health_permissions(client: TestClient) -> None:
    owner = create_authenticated_user(client, "permission.self@example.com")
    group = create_group(client, owner)
    response = client.get(
        f"/family-groups/{group['family_group_id']}/members/"
        f"{owner['user_id']}/permissions",
        headers=owner["headers"],
    )
    assert response.status_code == 200
    assert all(item["can_view"] is False for item in response.json())


def test_owner_cannot_change_another_members_sharing_choices(
    client: TestClient,
) -> None:
    owner = create_authenticated_user(client, "choice.owner@example.com")
    member = create_authenticated_user(client, "choice.member@example.com")
    group = create_group(client, owner)
    add_and_activate_member(client, group, owner, member)

    response = client.put(
        f"/family-groups/{group['family_group_id']}/members/"
        f"{member['user_id']}/permissions",
        json={
            "permissions": [
                {"data_type": "ALLERGIES", "can_view": True, "can_edit": True}
            ]
        },
        headers=owner["headers"],
    )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "PERMISSION_ACCESS_DENIED"


def test_left_member_cannot_manage_permissions(client: TestClient) -> None:
    owner = create_authenticated_user(client, "left.owner@example.com")
    member = create_authenticated_user(client, "left.member@example.com")
    group = create_group(client, owner)
    add_and_activate_member(client, group, owner, member)
    client.post(
        f"/family-groups/{group['family_group_id']}/members/{member['user_id']}/leave",
        headers=member["headers"],
    )

    response = set_permission(
        client, group, member, "ALLERGIES", can_view=True, can_edit=False
    )
    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "MEMBERSHIP_NOT_ACTIVE"
