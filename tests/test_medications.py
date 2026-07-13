from fastapi.testclient import TestClient

from app import schemas
from app.main import app
from app.routes.medications import get_rxnorm_service
from app.services.rxnorm import (
    IncompleteRxNormResponseError,
    MedicationNotFoundError,
    RxNormTimeoutError,
    RxNormUnavailableError,
)


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


class FailingRxNormService:
    def __init__(self, error: Exception) -> None:
        self.error = error

    def search_medication(self, drug_name: str) -> schemas.MedicationSearchResponse:
        raise self.error


def test_medication_search_returns_structured_response(client: TestClient) -> None:
    app.dependency_overrides[get_rxnorm_service] = SuccessfulRxNormService

    response = client.get("/medications/search", params={"name": "  aspirin  "})

    assert response.status_code == 200
    assert response.json() == {
        "query": "aspirin",
        "normalized_name": "aspirin",
        "rxcui": "1191",
        "active_ingredients": [{"rxcui": "1191", "name": "aspirin"}],
        "ingredient_data_complete": True,
        "disclaimer": (
            "RxNorm data identifies medication concepts and ingredients only. "
            "This response does not determine whether a medication is safe."
        ),
    }


def test_medication_search_validates_name(client: TestClient) -> None:
    app.dependency_overrides[get_rxnorm_service] = SuccessfulRxNormService

    assert client.get("/medications/search").status_code == 422
    assert client.get("/medications/search", params={"name": "   "}).status_code == 422
    assert client.get(
        "/medications/search",
        params={"name": "x" * 101},
    ).status_code == 422


def test_medication_service_errors_map_to_clear_http_responses(
    client: TestClient,
) -> None:
    cases = [
        (MedicationNotFoundError(), 404, "Medication not found in RxNorm"),
        (RxNormTimeoutError(), 504, "RxNorm did not respond before the timeout"),
        (
            IncompleteRxNormResponseError(),
            502,
            "RxNorm returned an incomplete response",
        ),
        (RxNormUnavailableError(), 502, "RxNorm is currently unavailable"),
    ]

    for error, expected_status, expected_detail in cases:
        app.dependency_overrides[get_rxnorm_service] = lambda error=error: (
            FailingRxNormService(error)
        )
        response = client.get("/medications/search", params={"name": "aspirin"})
        assert response.status_code == expected_status
        assert response.json() == {"detail": expected_detail}
