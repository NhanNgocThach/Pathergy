import hashlib
import hmac
import secrets
import threading
import time
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher, Type
from argon2.exceptions import InvalidHashError, VerificationError

from app.auth_config import AuthSettings
from app.errors import ServiceError

password_hasher = PasswordHasher(type=Type.ID)


def validate_password_strength(password: str, confirmation: str) -> None:
    if password != confirmation:
        raise ServiceError(422, "PASSWORD_MISMATCH", "Passwords do not match")
    valid = (
        len(password) >= 10
        and any(character.isupper() for character in password)
        and any(character.islower() for character in password)
        and any(character.isdigit() for character in password)
        and any(
            not character.isalnum() and not character.isspace()
            for character in password
        )
    )
    if not valid:
        raise ServiceError(
            422,
            "PASSWORD_TOO_WEAK",
            "Password must be at least 10 characters and include uppercase, "
            "lowercase, number, and special characters",
        )


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password_hash: str | None, password: str) -> bool:
    if password_hash is None:
        return False
    try:
        return password_hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False


def needs_password_rehash(password_hash: str) -> bool:
    return password_hasher.check_needs_rehash(password_hash)


def hash_opaque_token(token: str, secret: str) -> str:
    return hmac.new(
        secret.encode("utf-8"),
        token.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def new_opaque_token() -> tuple[str, str]:
    token_id = str(uuid.uuid4())
    return token_id, f"{token_id}.{secrets.token_urlsafe(32)}"


def token_id_from_opaque_token(token: str) -> str | None:
    token_id, separator, secret = token.partition(".")
    if not separator or not secret:
        return None
    try:
        return str(uuid.UUID(token_id))
    except ValueError:
        return None


def constant_time_hash_matches(expected_hash: str, actual_hash: str) -> bool:
    return secrets.compare_digest(expected_hash, actual_hash)


def create_access_token(
    user_id: int,
    session_id: str,
    settings: AuthSettings,
) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "sid": session_id,
        "type": "access",
        "jti": str(uuid.uuid4()),
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_minutes),
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str, settings: AuthSettings) -> dict[str, object]:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
            options={"require": ["sub", "sid", "type", "exp", "iat", "jti"]},
        )
    except jwt.ExpiredSignatureError as error:
        raise ServiceError(401, "ACCESS_TOKEN_EXPIRED", "Access token has expired") from error
    except jwt.PyJWTError as error:
        raise ServiceError(401, "INVALID_ACCESS_TOKEN", "Access token is invalid") from error
    if payload.get("type") != "access":
        raise ServiceError(401, "INVALID_ACCESS_TOKEN", "Access token is invalid")
    return payload


class InMemoryRateLimiter:
    """Small development hook; production needs a shared rate-limit store."""

    max_keys = 10_000

    def __init__(self) -> None:
        self._events: dict[str, list[float]] = {}
        self._lock = threading.Lock()
        self._last_cleanup = 0.0

    def _remove_expired_keys(self, cutoff: float) -> None:
        if cutoff - self._last_cleanup < 60:
            return
        self._events = {
            key: [event for event in events if event >= cutoff]
            for key, events in self._events.items()
            if any(event >= cutoff for event in events)
        }
        self._last_cleanup = cutoff

    def check(
        self,
        key: str,
        limit: int,
        *,
        capacity_message: str = (
            "Authentication rate-limit capacity was reached; try again later"
        ),
        limit_message: str = "Too many authentication requests; try again later",
    ) -> None:
        now = time.monotonic()
        cutoff = now - 60
        with self._lock:
            self._remove_expired_keys(cutoff)
            if key not in self._events and len(self._events) >= self.max_keys:
                raise ServiceError(
                    429,
                    "RATE_LIMIT_EXCEEDED",
                    capacity_message,
                )
            events = [event for event in self._events.get(key, []) if event >= cutoff]
            if len(events) >= limit:
                raise ServiceError(
                    429,
                    "RATE_LIMIT_EXCEEDED",
                    limit_message,
                )
            events.append(now)
            self._events[key] = events

    def clear(self) -> None:
        with self._lock:
            self._events.clear()
            self._last_cleanup = 0.0


auth_rate_limiter = InMemoryRateLimiter()
