from fastapi.testclient import TestClient


def create_user(client: TestClient, number: int) -> dict:
    return client.post(
        "/users",
        json={
            "email": f"fictional.permission{number}@example.com",
            "display_name": f"Permission Person {number}",
            "profile": {
                "first_name": f"Permission{number}",
                "last_name": "Fictional",
                "date_of_birth": "1991-02-03",
            },
        },
    ).json()


def create_group_with_active_member(
    client: TestClient,
    owner: dict,
    member: dict,
    name: str,
) -> dict:
    group = client.post(
        "/family-groups",
        json={"requesting_user_id": owner["user_id"], "name": name},
    ).json()
    client.post(
        f"/family-groups/{group['family_group_id']}/members",
        json={
            "requesting_user_id": owner["user_id"],
            "user_id": member["user_id"],
            "relationship": "RELATIVE",
        },
    )
    client.put(
        f"/family-groups/{group['family_group_id']}/members/{member['user_id']}",
        json={"requesting_user_id": owner["user_id"], "status": "ACTIVE"},
    )
    return group


def update_permission(
    client: TestClient,
    group_id: int,
    user_id: int,
    data_type: str,
    can_view: bool,
):
    return client.put(
        f"/family-groups/{group_id}/members/{user_id}/permissions",
        json={
            "requesting_user_id": user_id,
            "permissions": [
                {
                    "data_type": data_type,
                    "can_view": can_view,
                    "can_edit": False,
                }
            ],
        },
    )


def test_permissions_are_separate_for_each_family_membership(
    client: TestClient,
) -> None:
    owner = create_user(client, 1)
    member = create_user(client, 2)
    group_a = create_group_with_active_member(client, owner, member, "Family A")
    group_b = create_group_with_active_member(client, owner, member, "Family B")

    assert update_permission(
        client,
        group_a["family_group_id"],
        member["user_id"],
        "ALLERGIES",
        True,
    ).status_code == 200
    assert update_permission(
        client,
        group_b["family_group_id"],
        member["user_id"],
        "SCREENING_HISTORY",
        True,
    ).status_code == 200

    permissions_a = client.get(
        f"/family-groups/{group_a['family_group_id']}/members/{member['user_id']}/permissions",
        params={"requesting_user_id": member["user_id"]},
    ).json()
    permissions_b = client.get(
        f"/family-groups/{group_b['family_group_id']}/members/{member['user_id']}/permissions",
        params={"requesting_user_id": member["user_id"]},
    ).json()
    values_a = {item["data_type"]: item["can_view"] for item in permissions_a}
    values_b = {item["data_type"]: item["can_view"] for item in permissions_b}

    assert len(permissions_a) == 6
    assert values_a["ALLERGIES"] is True
    assert values_a["SCREENING_HISTORY"] is False
    assert values_b["ALLERGIES"] is False
    assert values_b["SCREENING_HISTORY"] is True


def test_group_owner_does_not_receive_automatic_health_access(
    client: TestClient,
) -> None:
    owner = create_user(client, 1)
    group = client.post(
        "/family-groups",
        json={"requesting_user_id": owner["user_id"], "name": "Family A"},
    ).json()

    permissions = client.get(
        f"/family-groups/{group['family_group_id']}/members/{owner['user_id']}/permissions",
        params={"requesting_user_id": owner["user_id"]},
    ).json()

    assert len(permissions) == 6
    assert all(permission["can_view"] is False for permission in permissions)
    assert all(permission["can_edit"] is False for permission in permissions)


def test_owner_cannot_change_another_members_permissions(client: TestClient) -> None:
    owner = create_user(client, 1)
    member = create_user(client, 2)
    group = create_group_with_active_member(client, owner, member, "Family A")

    response = client.put(
        f"/family-groups/{group['family_group_id']}/members/{member['user_id']}/permissions",
        json={
            "requesting_user_id": owner["user_id"],
            "permissions": [
                {"data_type": "ALLERGIES", "can_view": True, "can_edit": True}
            ],
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "PERMISSION_ACCESS_DENIED"


def test_left_membership_cannot_use_permissions(client: TestClient) -> None:
    owner = create_user(client, 1)
    member = create_user(client, 2)
    group = create_group_with_active_member(client, owner, member, "Family A")
    client.post(
        f"/family-groups/{group['family_group_id']}/members/{member['user_id']}/leave",
        json={"requesting_user_id": member["user_id"]},
    )

    response = client.get(
        f"/family-groups/{group['family_group_id']}/members/{member['user_id']}/permissions",
        params={"requesting_user_id": member["user_id"]},
    )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "MEMBERSHIP_NOT_ACTIVE"


def test_invalid_permission_type_is_rejected(client: TestClient) -> None:
    owner = create_user(client, 1)
    group = client.post(
        "/family-groups",
        json={"requesting_user_id": owner["user_id"], "name": "Family A"},
    ).json()

    response = update_permission(
        client,
        group["family_group_id"],
        owner["user_id"],
        "UNSUPPORTED_DATA",
        True,
    )

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "INVALID_PERMISSION_TYPE"
