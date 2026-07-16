from fastapi.testclient import TestClient

from app import schemas
from app.main import app
from app.routes.medications import get_dailymed_service, get_rxnorm_service
from app.services.dailymed import (
    DailyMedTimeoutError,
    DailyMedUnavailableError,
    IncompleteDailyMedResponseError,
)
from app.services.rxnorm import (
    IncompleteRxNormResponseError,
    MedicationNotFoundError,
    RxNormTimeoutError,
    RxNormUnavailableError,
)


class SuccessfulRxNormService:
    def suggest_medications(
        self,
        query: str,
        limit: int,
    ) -> list[schemas.MedicationSuggestion]:
        return [
            schemas.MedicationSuggestion(rxcui="161", name="acetaminophen", rank=1),
            schemas.MedicationSuggestion(rxcui="5640", name="ibuprofen", rank=2),
        ][:limit]

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

    def suggest_medications(
        self,
        query: str,
        limit: int,
    ) -> list[schemas.MedicationSuggestion]:
        raise self.error


class SuccessfulDailyMedService:
    def find_labels(
        self,
        rxcui: str,
        limit: int = 5,
    ) -> tuple[list[schemas.DailyMedLabelReference], bool]:
        assert rxcui == "1191"
        assert limit == 5
        return [
            schemas.DailyMedLabelReference(
                set_id="11111111-2222-3333-4444-555555555555",
                title="FICTIONAL ASPIRIN LABEL",
                published_date="Jul 10, 2026",
                version="3",
                url=(
                    "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid="
                    "11111111-2222-3333-4444-555555555555"
                ),
            )
        ], True


class FailingDailyMedService:
    def __init__(self, error: Exception) -> None:
        self.error = error

    def find_labels(
        self,
        rxcui: str,
        limit: int = 5,
    ) -> tuple[list[schemas.DailyMedLabelReference], bool]:
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


def test_medication_details_combines_rxnorm_and_dailymed(
    client: TestClient,
) -> None:
    app.dependency_overrides[get_rxnorm_service] = SuccessfulRxNormService
    app.dependency_overrides[get_dailymed_service] = SuccessfulDailyMedService

    response = client.get("/medications/details", params={"name": " aspirin "})

    assert response.status_code == 200
    data = response.json()
    assert data["normalized_name"] == "aspirin"
    assert data["active_ingredients"] == [{"rxcui": "1191", "name": "aspirin"}]
    assert data["dailymed"]["status"] == "AVAILABLE"
    assert data["dailymed"]["labels"] == [
        {
            "set_id": "11111111-2222-3333-4444-555555555555",
            "title": "FICTIONAL ASPIRIN LABEL",
            "published_date": "Jul 10, 2026",
            "version": "3",
            "url": (
                "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid="
                "11111111-2222-3333-4444-555555555555"
            ),
        }
    ]
    assert "different brands" in data["dailymed"]["disclaimer"]


def test_medication_details_returns_not_found_when_no_labels_exist(
    client: TestClient,
) -> None:
    class EmptyDailyMedService:
        def find_labels(self, rxcui: str, limit: int = 5):
            return [], True

    app.dependency_overrides[get_rxnorm_service] = SuccessfulRxNormService
    app.dependency_overrides[get_dailymed_service] = EmptyDailyMedService

    response = client.get("/medications/details", params={"name": "aspirin"})

    assert response.status_code == 200
    assert response.json()["dailymed"]["status"] == "NOT_FOUND"
    assert response.json()["dailymed"]["labels"] == []


def test_medication_details_keeps_rxnorm_data_when_dailymed_fails(
    client: TestClient,
) -> None:
    cases = [
        (DailyMedTimeoutError(), "UNAVAILABLE", "timeout"),
        (DailyMedUnavailableError(), "UNAVAILABLE", "unavailable"),
        (IncompleteDailyMedResponseError(), "INCOMPLETE", "incomplete"),
    ]
    for error, expected_status, expected_message in cases:
        app.dependency_overrides[get_rxnorm_service] = SuccessfulRxNormService
        app.dependency_overrides[get_dailymed_service] = lambda error=error: (
            FailingDailyMedService(error)
        )

        response = client.get("/medications/details", params={"name": "aspirin"})

        assert response.status_code == 200
        assert response.json()["normalized_name"] == "aspirin"
        assert response.json()["dailymed"]["status"] == expected_status
        assert expected_message in response.json()["dailymed"]["message"].lower()


def test_medication_details_validates_name(client: TestClient) -> None:
    app.dependency_overrides[get_rxnorm_service] = SuccessfulRxNormService
    app.dependency_overrides[get_dailymed_service] = SuccessfulDailyMedService

    assert client.get("/medications/details").status_code == 422
    assert client.get(
        "/medications/details",
        params={"name": " "},
    ).status_code == 422


def test_medication_suggestions_return_limited_prefix_matches(
    client: TestClient,
) -> None:
    app.dependency_overrides[get_rxnorm_service] = SuccessfulRxNormService

    response = client.get(
        "/medications/suggestions",
        params={"q": "  acet  ", "limit": 1},
    )

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": {
            "query": "acet",
            "suggestions": [
                {"rxcui": "161", "name": "acetaminophen", "rank": 1}
            ],
        },
        "message": "Medication suggestions retrieved successfully.",
    }


def test_medication_suggestions_validate_query_and_limit(client: TestClient) -> None:
    app.dependency_overrides[get_rxnorm_service] = SuccessfulRxNormService

    assert client.get("/medications/suggestions").status_code == 422
    assert client.get(
        "/medications/suggestions",
        params={"q": " ", "limit": 8},
    ).status_code == 422
    assert client.get(
        "/medications/suggestions",
        params={"q": "acet", "limit": 11},
    ).status_code == 422


def test_medication_suggestion_errors_use_rxnorm_conventions(
    client: TestClient,
) -> None:
    cases = [
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
        response = client.get("/medications/suggestions", params={"q": "acet"})
        assert response.status_code == expected_status
        assert response.json() == {"detail": expected_detail}


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
