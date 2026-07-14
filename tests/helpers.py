from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient


PASSWORD = "StrongPass1!"


def create_authenticated_user(
    client: TestClient,
    email: str,
    *,
    first_name: str = "Fictional",
) -> dict:
    registration = client.post(
        "/auth/register",
        json={
            "email": email,
            "display_name": f"{first_name} Person",
            "password": PASSWORD,
            "confirm_password": PASSWORD,
            "profile": {
                "first_name": first_name,
                "last_name": "Person",
                "date_of_birth": "1990-01-01",
            },
        },
    )
    assert registration.status_code == 201, registration.text
    user = registration.json()
    token = parse_qs(urlparse(user["verification_url"]).query)["token"][0]
    assert client.post("/auth/verify-email", json={"token": token}).status_code == 200
    login = client.post(
        "/auth/login",
        json={"email": email, "password": PASSWORD},
    )
    assert login.status_code == 200, login.text
    user["headers"] = {
        "Authorization": f"Bearer {login.json()['access_token']}"
    }
    return user


def create_group(client: TestClient, user: dict, name: str = "Fictional Family") -> dict:
    response = client.post(
        "/family-groups",
        json={"name": name},
        headers=user["headers"],
    )
    assert response.status_code == 201, response.text
    return response.json()


def add_and_activate_member(
    client: TestClient,
    group: dict,
    manager: dict,
    member: dict,
    *,
    role: str = "MEMBER",
) -> None:
    group_id = group["family_group_id"]
    added = client.post(
        f"/family-groups/{group_id}/members",
        json={
            "user_id": member["user_id"],
            "role": role,
            "relationship": "RELATIVE",
        },
        headers=manager["headers"],
    )
    assert added.status_code == 201, added.text
    activated = client.put(
        f"/family-groups/{group_id}/members/{member['user_id']}",
        json={"status": "ACTIVE"},
        headers=manager["headers"],
    )
    assert activated.status_code == 200, activated.text


def set_permission(
    client: TestClient,
    group: dict,
    member: dict,
    data_type: str,
    *,
    can_view: bool,
    can_edit: bool,
):
    return client.put(
        f"/family-groups/{group['family_group_id']}/members/"
        f"{member['user_id']}/permissions",
        json={
            "permissions": [
                {
                    "data_type": data_type,
                    "can_view": can_view,
                    "can_edit": can_edit,
                }
            ]
        },
        headers=member["headers"],
    )
