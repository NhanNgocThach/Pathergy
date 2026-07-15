from fastapi.testclient import TestClient

from app import schemas
from app.main import app
from app.routes.medications import get_rxnorm_service


class SuccessfulRxNormService:
    def search_medication(self, drug_name: str) -> schemas.MedicationSearchResponse:
        return schemas.MedicationSearchResponse(
            query=drug_name,
            normalized_name="aspirin",
            rxcui="1191",
            active_ingredients=[
                schemas.MedicationIngredient(rxcui="1191", name="aspirin")
            ],
            ingredient_data_complete=True,
        )


def test_api_responses_include_browser_security_headers(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert "camera=()" in response.headers["permissions-policy"]
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]


def test_sensitive_responses_are_not_cached(client: TestClient) -> None:
    response = client.get("/patients")

    assert response.status_code == 401
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["pragma"] == "no-cache"


def test_swagger_csp_allows_only_its_required_documentation_assets(
    client: TestClient,
) -> None:
    response = client.get("/docs")

    assert response.status_code == 200
    policy = response.headers["content-security-policy"]
    assert "script-src 'self' https://cdn.jsdelivr.net" in policy
    assert "frame-ancestors 'none'" in policy


def test_oversized_request_body_is_rejected_before_validation(
    client: TestClient,
) -> None:
    response = client.post(
        "/auth/register",
        content=b"x" * 65_537,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 413
    assert response.json() == {
        "detail": {
            "code": "REQUEST_TOO_LARGE",
            "message": "Request body exceeds the configured limit",
        }
    }


def test_public_medication_endpoint_is_rate_limited(
    client: TestClient,
    monkeypatch,
) -> None:
    monkeypatch.setenv("PUBLIC_API_RATE_LIMIT_PER_MINUTE", "1")
    app.dependency_overrides[get_rxnorm_service] = SuccessfulRxNormService

    first = client.get("/medications/search", params={"name": "aspirin"})
    second = client.get("/medications/search", params={"name": "aspirin"})

    assert first.status_code != 429
    assert second.status_code == 429
    assert second.json()["detail"]["code"] == "RATE_LIMIT_EXCEEDED"
