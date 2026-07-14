from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app import models
from app.auth_config import get_auth_settings
from app.errors import ServiceError
from tests.helpers import create_authenticated_user

PASSWORD = "StrongPass1!"
NEW_PASSWORD = "NewStrong2@"


def registration_payload(email: str = "auth.person@example.com") -> dict:
    return {
        "email": email,
        "display_name": "Fictional Auth Person",
        "password": PASSWORD,
        "confirm_password": PASSWORD,
        "profile": {
            "first_name": "Fictional",
            "last_name": "Auth",
            "date_of_birth": "1990-01-01",
        },
    }


def token_from_url(url: str) -> str:
    return parse_qs(urlparse(url).query)["token"][0]


def register(client: TestClient, email: str = "auth.person@example.com") -> dict:
    response = client.post("/auth/register", json=registration_payload(email))
    assert response.status_code == 201
    return response.json()


def register_and_verify(
    client: TestClient,
    email: str = "auth.person@example.com",
) -> dict:
    registered = register(client, email)
    token = token_from_url(registered["verification_url"])
    response = client.post("/auth/verify-email", json={"token": token})
    assert response.status_code == 200
    return registered


def login(
    client: TestClient,
    email: str = "auth.person@example.com",
    password: str = PASSWORD,
    device_name: str = "Fictional laptop",
) -> dict:
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
            "device_name": device_name,
            "device_type": "desktop",
        },
        headers={"user-agent": "Pathergy-Test/1.0"},
    )
    assert response.status_code == 200
    return response.json()


def bearer(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


def test_registration_hashes_password_and_verification_token(
    client: TestClient,
    session_factory: sessionmaker[Session],
) -> None:
    registered = register(client)

    assert registered["verification_required"] is True
    assert registered["verification_url"] is not None
    assert "password" not in registered
    raw_token = token_from_url(registered["verification_url"])
    with session_factory() as db:
        user = db.scalar(select(models.UserAccount))
        verification = db.scalar(select(models.EmailVerificationToken))
        assert user is not None and user.password_hash is not None
        assert user.password_hash.startswith("$argon2id$")
        assert user.password_hash != PASSWORD
        assert verification is not None
        assert verification.token_hash != raw_token


def test_registration_rejects_duplicate_email_and_weak_password(
    client: TestClient,
) -> None:
    register(client)
    duplicate = client.post("/auth/register", json=registration_payload())
    weak_data = registration_payload("weak@example.com")
    weak_data.update(password="password", confirm_password="password")
    weak = client.post("/auth/register", json=weak_data)
    mismatch_data = registration_payload("mismatch@example.com")
    mismatch_data["confirm_password"] = "Different1!"
    mismatch = client.post("/auth/register", json=mismatch_data)
    invalid_email_data = registration_payload("valid@example.com")
    invalid_email_data["email"] = "not-an-email"
    invalid_email = client.post("/auth/register", json=invalid_email_data)

    assert duplicate.status_code == 409
    assert duplicate.json()["detail"]["code"] == "EMAIL_ALREADY_REGISTERED"
    assert weak.status_code == 422
    assert weak.json()["detail"]["code"] == "PASSWORD_TOO_WEAK"
    assert mismatch.json()["detail"]["code"] == "PASSWORD_MISMATCH"
    assert invalid_email.status_code == 422


def test_registration_cannot_claim_existing_patient_and_space_is_not_special(
    client: TestClient,
) -> None:
    actor = create_authenticated_user(client, "existing.creator@example.com")
    patient = client.post(
        "/patients",
        json={
            "first_name": "Existing",
            "last_name": "Patient",
            "date_of_birth": "1991-01-01",
        },
        headers=actor["headers"],
    ).json()
    claim_data = registration_payload("claim@example.com")
    claim_data.pop("profile")
    claim_data["patient_id"] = patient["id"]
    claim = client.post("/auth/register", json=claim_data)

    weak_data = registration_payload("space-special@example.com")
    weak_data.update(password="NoSpecial1 ", confirm_password="NoSpecial1 ")
    weak = client.post("/auth/register", json=weak_data)

    assert claim.status_code == 422
    assert weak.status_code == 422
    assert weak.json()["detail"]["code"] == "PASSWORD_TOO_WEAK"


def test_email_verification_is_required_and_single_use(client: TestClient) -> None:
    registered = register(client)
    before_verify = client.post(
        "/auth/login",
        json={"email": "auth.person@example.com", "password": PASSWORD},
    )
    token = token_from_url(registered["verification_url"])
    verified = client.post("/auth/verify-email", json={"token": token})
    reused = client.post("/auth/verify-email", json={"token": token})

    assert before_verify.status_code == 403
    assert before_verify.json()["detail"]["code"] == "EMAIL_NOT_VERIFIED"
    assert verified.status_code == 200
    assert reused.status_code == 400
    assert reused.json()["detail"]["code"] == "INVALID_VERIFICATION_TOKEN"


def test_expired_verification_token_is_rejected(
    client: TestClient,
    session_factory: sessionmaker[Session],
) -> None:
    registered = register(client)
    token = token_from_url(registered["verification_url"])
    with session_factory() as db:
        verification = db.scalar(select(models.EmailVerificationToken))
        verification.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        db.commit()

    response = client.post("/auth/verify-email", json={"token": token})

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "VERIFICATION_TOKEN_EXPIRED"


def test_login_returns_jwt_and_me_returns_current_user(
    client: TestClient,
    session_factory: sessionmaker[Session],
) -> None:
    registered = register_and_verify(client)
    tokens = login(client)

    assert tokens["token_type"] == "bearer"
    assert tokens["access_token_expires_in"] == 900
    assert tokens["refresh_token_expires_in"] == 2_592_000
    me = client.get("/auth/me", headers=bearer(tokens["access_token"]))
    assert me.status_code == 200
    assert me.json()["user_id"] == registered["user_id"]
    assert me.json()["email"] == "auth.person@example.com"
    assert "password_hash" not in me.json()
    with session_factory() as db:
        session = db.scalar(select(models.AuthSession))
        assert session is not None
        assert session.refresh_token_hash != tokens["refresh_token"]
        assert tokens["refresh_token"] not in session.refresh_token_hash

    lowercase_scheme = client.get(
        "/auth/me",
        headers={"Authorization": f"bearer {tokens['access_token']}"},
    )
    assert lowercase_scheme.status_code == 200


def test_openapi_declares_bearer_authentication(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()

    security_schemes = schema["components"]["securitySchemes"]
    assert security_schemes["HTTPBearer"] == {
        "type": "http",
        "scheme": "bearer",
    }
    assert schema["paths"]["/auth/me"]["get"]["security"] == [
        {"HTTPBearer": []}
    ]


def test_invalid_and_expired_access_tokens_have_stable_errors(
    client: TestClient,
) -> None:
    invalid = client.get("/auth/me", headers=bearer("not-a-jwt"))
    settings = get_auth_settings()
    now = datetime.now(timezone.utc)
    expired_token = jwt.encode(
        {
            "sub": "1",
            "sid": "00000000-0000-0000-0000-000000000000",
            "type": "access",
            "jti": "expired-test",
            "iat": now - timedelta(minutes=20),
            "exp": now - timedelta(minutes=5),
            "iss": settings.jwt_issuer,
            "aud": settings.jwt_audience,
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )
    expired = client.get("/auth/me", headers=bearer(expired_token))

    assert invalid.status_code == 401
    assert invalid.json()["detail"]["code"] == "INVALID_ACCESS_TOKEN"
    assert invalid.headers["www-authenticate"] == "Bearer"
    assert expired.status_code == 401
    assert expired.json()["detail"]["code"] == "ACCESS_TOKEN_EXPIRED"


def test_missing_access_token_has_authentication_required_error(
    client: TestClient,
) -> None:
    response = client.get("/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "AUTHENTICATION_REQUIRED"
    assert response.headers["www-authenticate"] == "Bearer"


def test_refresh_rotates_token_and_replay_revokes_session(client: TestClient) -> None:
    register_and_verify(client)
    original = login(client)
    rotated = client.post(
        "/auth/refresh",
        json={"refresh_token": original["refresh_token"]},
    )
    assert rotated.status_code == 200
    assert rotated.json()["refresh_token"] != original["refresh_token"]

    replay = client.post(
        "/auth/refresh",
        json={"refresh_token": original["refresh_token"]},
    )
    after_replay = client.post(
        "/auth/refresh",
        json={"refresh_token": rotated.json()["refresh_token"]},
    )

    assert replay.status_code == 401
    assert replay.json()["detail"]["code"] == "REFRESH_TOKEN_REVOKED"
    assert after_replay.json()["detail"]["code"] == "REFRESH_TOKEN_REVOKED"


def test_expired_and_invalid_refresh_tokens(
    client: TestClient,
    session_factory: sessionmaker[Session],
) -> None:
    register_and_verify(client)
    tokens = login(client)
    invalid = client.post("/auth/refresh", json={"refresh_token": "invalid"})
    with session_factory() as db:
        session = db.scalar(select(models.AuthSession))
        session.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        db.commit()
    expired = client.post(
        "/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )

    assert invalid.json()["detail"]["code"] == "INVALID_REFRESH_TOKEN"
    assert expired.json()["detail"]["code"] == "REFRESH_TOKEN_EXPIRED"


def test_forged_refresh_token_does_not_reveal_session_state(client: TestClient) -> None:
    register_and_verify(client)
    tokens = login(client)
    session_id = tokens["refresh_token"].split(".", maxsplit=1)[0]

    forged = client.post(
        "/auth/refresh",
        json={"refresh_token": f"{session_id}.not-the-real-secret"},
    )

    assert forged.status_code == 401
    assert forged.json()["detail"]["code"] == "INVALID_REFRESH_TOKEN"


def test_logout_revokes_current_session(client: TestClient) -> None:
    register_and_verify(client)
    tokens = login(client)
    headers = bearer(tokens["access_token"])

    assert client.post("/auth/logout", headers=headers).status_code == 204
    assert client.get("/auth/me", headers=headers).json()["detail"]["code"] == (
        "INVALID_ACCESS_TOKEN"
    )
    assert client.post(
        "/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    ).json()["detail"]["code"] == "REFRESH_TOKEN_REVOKED"


def test_session_listing_single_revocation_and_logout_all(client: TestClient) -> None:
    register_and_verify(client)
    laptop = login(client, device_name="Laptop")
    phone = login(client, device_name="Phone")
    phone_headers = bearer(phone["access_token"])

    sessions = client.get("/auth/sessions", headers=phone_headers)
    assert sessions.status_code == 200
    assert len(sessions.json()) == 2
    current = next(item for item in sessions.json() if item["is_current"])
    other = next(item for item in sessions.json() if not item["is_current"])
    assert current["device_name"] == "Phone"

    assert client.delete(
        f"/auth/sessions/{other['session_id']}",
        headers=phone_headers,
    ).status_code == 204
    assert client.post(
        "/auth/refresh",
        json={"refresh_token": laptop["refresh_token"]},
    ).json()["detail"]["code"] == "REFRESH_TOKEN_REVOKED"

    assert client.delete("/auth/sessions", headers=phone_headers).status_code == 204
    assert client.get("/auth/me", headers=phone_headers).status_code == 401


def test_user_cannot_revoke_another_users_session(client: TestClient) -> None:
    register_and_verify(client, "first.session@example.com")
    first_tokens = login(client, "first.session@example.com")
    first_session_id = first_tokens["refresh_token"].split(".", maxsplit=1)[0]

    register_and_verify(client, "second.session@example.com")
    second_tokens = login(client, "second.session@example.com")
    response = client.delete(
        f"/auth/sessions/{first_session_id}",
        headers=bearer(second_tokens["access_token"]),
    )

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "SESSION_NOT_FOUND"
    assert client.get(
        "/auth/me",
        headers=bearer(first_tokens["access_token"]),
    ).status_code == 200


def test_authenticated_requests_throttle_session_activity_writes(
    client: TestClient,
    session_factory: sessionmaker[Session],
) -> None:
    register_and_verify(client)
    tokens = login(client)
    with session_factory() as db:
        before = db.scalar(select(models.AuthSession)).last_used_at

    assert client.get("/auth/me", headers=bearer(tokens["access_token"])).status_code == 200

    with session_factory() as db:
        after = db.scalar(select(models.AuthSession)).last_used_at
    assert after == before


def test_password_reset_changes_password_and_revokes_sessions(
    client: TestClient,
) -> None:
    register_and_verify(client)
    old_tokens = login(client)
    forgot = client.post(
        "/auth/forgot-password",
        json={"email": "auth.person@example.com"},
    )
    reset_token = token_from_url(forgot.json()["development_url"])
    reset = client.post(
        "/auth/reset-password",
        json={
            "token": reset_token,
            "new_password": NEW_PASSWORD,
            "confirm_password": NEW_PASSWORD,
        },
    )

    assert reset.status_code == 200
    assert client.get(
        "/auth/me",
        headers=bearer(old_tokens["access_token"]),
    ).status_code == 401
    old_login = client.post(
        "/auth/login",
        json={"email": "auth.person@example.com", "password": PASSWORD},
    )
    assert old_login.status_code == 401
    assert login(client, password=NEW_PASSWORD)["access_token"]
    reused = client.post(
        "/auth/reset-password",
        json={
            "token": reset_token,
            "new_password": PASSWORD,
            "confirm_password": PASSWORD,
        },
    )
    assert reused.json()["detail"]["code"] == "INVALID_RESET_TOKEN"


def test_expired_and_invalid_reset_tokens(
    client: TestClient,
    session_factory: sessionmaker[Session],
) -> None:
    register_and_verify(client)
    forgot = client.post(
        "/auth/forgot-password",
        json={"email": "auth.person@example.com"},
    )
    token = token_from_url(forgot.json()["development_url"])
    with session_factory() as db:
        reset = db.scalar(select(models.PasswordResetToken))
        assert reset.token_hash != token
        assert token not in reset.token_hash
        reset.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        db.commit()

    expired = client.post(
        "/auth/reset-password",
        json={
            "token": token,
            "new_password": NEW_PASSWORD,
            "confirm_password": NEW_PASSWORD,
        },
    )
    invalid = client.post(
        "/auth/reset-password",
        json={
            "token": "invalid",
            "new_password": NEW_PASSWORD,
            "confirm_password": NEW_PASSWORD,
        },
    )
    assert expired.json()["detail"]["code"] == "RESET_TOKEN_EXPIRED"
    assert invalid.json()["detail"]["code"] == "INVALID_RESET_TOKEN"


def test_change_password_revokes_sessions(client: TestClient) -> None:
    register_and_verify(client)
    tokens = login(client)
    response = client.post(
        "/auth/change-password",
        json={
            "current_password": PASSWORD,
            "new_password": NEW_PASSWORD,
            "confirm_password": NEW_PASSWORD,
        },
        headers=bearer(tokens["access_token"]),
    )

    assert response.status_code == 200
    assert client.get(
        "/auth/me",
        headers=bearer(tokens["access_token"]),
    ).status_code == 401
    assert login(client, password=NEW_PASSWORD)["access_token"]


def test_repeated_failed_logins_lock_account(client: TestClient) -> None:
    register_and_verify(client)
    for _ in range(4):
        response = client.post(
            "/auth/login",
            json={"email": "auth.person@example.com", "password": "WrongPass1!"},
        )
        assert response.status_code == 401

    locked = client.post(
        "/auth/login",
        json={"email": "auth.person@example.com", "password": "WrongPass1!"},
    )
    correct_but_locked = client.post(
        "/auth/login",
        json={"email": "auth.person@example.com", "password": PASSWORD},
    )
    assert locked.status_code == 423
    assert locked.json()["detail"]["code"] == "ACCOUNT_LOCKED"
    assert correct_but_locked.json()["detail"]["code"] == "ACCOUNT_LOCKED"


def test_malformed_stored_password_hash_is_handled_as_invalid_credentials(
    client: TestClient,
    session_factory: sessionmaker[Session],
) -> None:
    register_and_verify(client)
    with session_factory() as db:
        user = db.scalar(select(models.UserAccount))
        user.password_hash = "corrupt-hash"
        db.commit()

    response = client.post(
        "/auth/login",
        json={"email": "auth.person@example.com", "password": PASSWORD},
    )

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "INVALID_CREDENTIALS"


def test_invalid_rate_limit_configuration_has_stable_error(monkeypatch) -> None:
    monkeypatch.setenv("AUTH_RATE_LIMIT_PER_MINUTE", "0")

    with pytest.raises(ServiceError) as raised:
        get_auth_settings()

    assert raised.value.code == "AUTH_CONFIGURATION_ERROR"


def test_login_rate_limit_hook_returns_429(
    client: TestClient,
    monkeypatch,
) -> None:
    monkeypatch.setenv("AUTH_RATE_LIMIT_PER_MINUTE", "2")
    payload = {"email": "missing@example.com", "password": "WrongPass1!"}

    assert client.post("/auth/login", json=payload).status_code == 401
    assert client.post("/auth/login", json=payload).status_code == 401
    limited = client.post("/auth/login", json=payload)

    assert limited.status_code == 429
    assert limited.json()["detail"]["code"] == "RATE_LIMIT_EXCEEDED"
    assert limited.headers["retry-after"] == "60"
