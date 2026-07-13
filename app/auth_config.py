import os
from dataclasses import dataclass

from dotenv import load_dotenv

from app.errors import ServiceError

load_dotenv()


@dataclass(frozen=True)
class AuthSettings:
    jwt_secret: str
    token_hash_secret: str
    development_mode: bool
    development_base_url: str
    access_token_minutes: int = 15
    refresh_token_days: int = 30
    verification_token_hours: int = 24
    reset_token_hours: int = 1
    max_failed_logins: int = 5
    lockout_minutes: int = 15
    rate_limit_per_minute: int = 30
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "pathergy"
    jwt_audience: str = "pathergy-api"


def _required_secret(name: str) -> str:
    value = os.getenv(name, "")
    if len(value) < 32:
        raise ServiceError(
            500,
            "AUTH_CONFIGURATION_ERROR",
            f"{name} must be configured with at least 32 characters",
        )
    return value


def _positive_integer(name: str, default: str) -> int:
    raw_value = os.getenv(name, default)
    try:
        value = int(raw_value)
    except ValueError as error:
        raise ServiceError(
            500,
            "AUTH_CONFIGURATION_ERROR",
            f"{name} must be a positive integer",
        ) from error
    if value < 1:
        raise ServiceError(
            500,
            "AUTH_CONFIGURATION_ERROR",
            f"{name} must be a positive integer",
        )
    return value


def get_auth_settings() -> AuthSettings:
    return AuthSettings(
        jwt_secret=_required_secret("AUTH_JWT_SECRET"),
        token_hash_secret=_required_secret("AUTH_TOKEN_HASH_SECRET"),
        development_mode=os.getenv("AUTH_DEVELOPMENT_MODE", "false").lower()
        in {"1", "true", "yes"},
        development_base_url=os.getenv(
            "AUTH_DEVELOPMENT_BASE_URL",
            "http://127.0.0.1:8000",
        ).rstrip("/"),
        rate_limit_per_minute=_positive_integer("AUTH_RATE_LIMIT_PER_MINUTE", "30"),
    )
