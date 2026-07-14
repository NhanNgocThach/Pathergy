import os


def get_cors_allowed_origins() -> list[str]:
    """Return the explicit browser origins allowed to call the API."""
    raw_origins = os.getenv("CORS_ALLOWED_ORIGINS", "")
    origins = [
        origin.strip().rstrip("/")
        for origin in raw_origins.split(",")
        if origin.strip()
    ]
    if "*" in origins:
        raise RuntimeError(
            "CORS_ALLOWED_ORIGINS must list explicit browser origins; '*' is forbidden"
        )
    return list(dict.fromkeys(origins))
