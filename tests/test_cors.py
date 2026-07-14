import pytest

from app.cors_config import get_cors_allowed_origins


def test_cors_origins_are_explicit_and_normalized(monkeypatch) -> None:
    monkeypatch.setenv(
        "CORS_ALLOWED_ORIGINS",
        " http://localhost:3000/, http://127.0.0.1:3000 ",
    )

    assert get_cors_allowed_origins() == [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


def test_cors_is_disabled_without_an_allowlist(monkeypatch) -> None:
    monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)
    assert get_cors_allowed_origins() == []


def test_cors_rejects_wildcard_origins(monkeypatch) -> None:
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "*")

    with pytest.raises(RuntimeError, match="explicit browser origins"):
        get_cors_allowed_origins()
