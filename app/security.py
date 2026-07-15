import hashlib
import os

from fastapi import Request
from starlette.responses import Response

from app.errors import ServiceError
from app.services.auth_security import InMemoryRateLimiter

DEFAULT_MAX_REQUEST_BODY_BYTES = 64 * 1024
DEFAULT_PUBLIC_RATE_LIMIT_PER_MINUTE = 120

public_api_rate_limiter = InMemoryRateLimiter()


def _positive_environment_integer(name: str, default: int) -> int:
    raw_value = os.getenv(name, str(default))
    try:
        value = int(raw_value)
    except ValueError as error:
        raise RuntimeError(f"{name} must be a positive integer") from error
    if value < 1:
        raise RuntimeError(f"{name} must be a positive integer")
    return value


def maximum_request_body_bytes() -> int:
    return _positive_environment_integer(
        "MAX_REQUEST_BODY_BYTES",
        DEFAULT_MAX_REQUEST_BODY_BYTES,
    )


def check_public_api_rate_limit(request: Request) -> None:
    """Limit costly public RxNorm requests without retaining a raw IP address."""
    client_host = request.client.host if request.client else "unknown"
    anonymous_client = hashlib.sha256(client_host.encode("utf-8")).hexdigest()
    key = f"public:{request.url.path}:{anonymous_client}"
    limit = _positive_environment_integer(
        "PUBLIC_API_RATE_LIMIT_PER_MINUTE",
        DEFAULT_PUBLIC_RATE_LIMIT_PER_MINUTE,
    )
    public_api_rate_limiter.check(
        key,
        limit,
        capacity_message="Public API rate-limit capacity was reached; try again later",
        limit_message="Too many public API requests; try again later",
    )


def add_security_headers(request: Request, response: Response) -> None:
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=(), payment=()"
    )
    if request.url.path in {"/docs", "/redoc"}:
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; script-src 'self' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https://fastapi.tiangolo.com; "
            "connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; "
            "form-action 'none'"
        )
    else:
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; "
            "form-action 'none'"
        )

    forwarded_protocol = request.headers.get("x-forwarded-proto", "")
    if request.url.scheme == "https" or forwarded_protocol == "https":
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

    sensitive_prefixes = (
        "/auth",
        "/patients",
        "/users",
        "/family-groups",
    )
    if request.headers.get("authorization") or request.url.path.startswith(
        sensitive_prefixes
    ):
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
