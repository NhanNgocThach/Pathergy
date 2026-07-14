from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app import models, schemas
from app.main import app
from app.routes.medications import get_rxnorm_service
from app.services.rxnorm import MedicationNotFoundError, RxNormTimeoutError
from app.services.screening import normalize_text
from tests.helpers import create_authenticated_user


class FakeRxNormService:
    def __init__(
        self,
        result: schemas.MedicationSearchResponse | None = None,
        error: Exception | None = None,
    ) -> None:
        self.result = result
        self.error = error

    def search_medication(self, drug_name: str) -> schemas.MedicationSearchResponse:
        if self.error is not None:
            raise self.error
        assert self.result is not None
        return self.result.model_copy(update={"query": drug_name})


def medication_result(
    ingredients: list[tuple[str, str]],
    *,
    query: str = "Example medication",
    normalized_name: str = "Example normalized medication",
    complete: bool = True,
) -> schemas.MedicationSearchResponse:
    return schemas.MedicationSearchResponse(
        query=query,
        normalized_name=normalized_name,
        rxcui="99999",
        active_ingredients=[
            schemas.MedicationIngredient(rxcui=rxcui, name=name)
            for rxcui, name in ingredients
        ],
        ingredient_data_complete=complete,
    )


def set_rxnorm_result(result: schemas.MedicationSearchResponse) -> None:
    app.dependency_overrides[get_rxnorm_service] = lambda: FakeRxNormService(
        result=result
    )


def create_patient(client: TestClient) -> int:
    user = create_authenticated_user(client, "screening.owner@example.com")
    client.headers.update(user["headers"])
    return user["patient_id"]


def add_allergy(
    client: TestClient,
    patient_id: int,
    substance: str,
    rxcui: str | None = None,
) -> int:
    response = client.post(
        f"/patients/{patient_id}/allergies",
        json={
            "substance": substance,
            "rxcui": rxcui,
            "reaction": "Fictional example reaction",
            "severity": "moderate",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def check(client: TestClient, patient_id: int, name: str = "Example"):
    return client.post(
        f"/patients/{patient_id}/medication-check",
        json={"medication_name": name},
    )


def test_exact_rxcui_match_takes_priority(client: TestClient) -> None:
    patient_id = create_patient(client)
    add_allergy(client, patient_id, "Different display name", rxcui="723")
    set_rxnorm_result(medication_result([("723", "amoxicillin")]))

    response = check(client, patient_id)

    assert response.status_code == 200
    assert response.json()["result"] == "POTENTIAL_ALLERGY_MATCH"
    assert response.json()["matches"][0]["match_method"] == "RXCUI"


def test_brand_name_uses_normalized_ingredient_text_fallback(
    client: TestClient,
) -> None:
    patient_id = create_patient(client)
    add_allergy(client, patient_id, "  AMOXICILLIN  ")
    set_rxnorm_result(
        medication_result(
            [("723", "amoxicillin")],
            query="Augmentin",
            normalized_name="amoxicillin / clavulanate potassium",
        )
    )

    response = check(client, patient_id, "Augmentin")

    assert response.json()["result"] == "POTENTIAL_ALLERGY_MATCH"
    assert response.json()["normalized_medication_name"] == (
        "amoxicillin / clavulanate potassium"
    )
    assert response.json()["matches"][0]["match_method"] == "NORMALIZED_TEXT"


def test_text_normalization_handles_case_and_repeated_spaces() -> None:
    assert normalize_text("  Amoxicillin   Sodium  ") == "amoxicillin sodium"


def test_multiple_ingredients_are_all_compared(client: TestClient) -> None:
    patient_id = create_patient(client)
    add_allergy(client, patient_id, "clavulanate-potassium")
    set_rxnorm_result(
        medication_result(
            [("723", "amoxicillin"), ("21212", "clavulanate potassium")]
        )
    )

    response = check(client, patient_id)

    assert len(response.json()["active_ingredients"]) == 2
    assert response.json()["result"] == "POTENTIAL_ALLERGY_MATCH"
    assert response.json()["matches"][0]["ingredient_rxcui"] == "21212"


def test_conflicting_rxcui_does_not_fall_back_to_equal_text(
    client: TestClient,
) -> None:
    patient_id = create_patient(client)
    add_allergy(client, patient_id, "amoxicillin", rxcui="111")
    set_rxnorm_result(medication_result([("723", "amoxicillin")]))

    response = check(client, patient_id)

    assert response.json()["result"] == "NO_RECORDED_MATCH_FOUND"
    assert response.json()["matches"] == []


def test_no_allergies_returns_no_recorded_match_and_stores_history(
    client: TestClient,
    session_factory: sessionmaker[Session],
) -> None:
    patient_id = create_patient(client)
    set_rxnorm_result(medication_result([("1191", "aspirin")]))

    response = check(client, patient_id, "Aspirin")

    assert response.json()["result"] == "NO_RECORDED_MATCH_FOUND"
    assert response.json()["matches"] == []
    with session_factory() as db:
        history = db.scalar(select(models.SearchHistory))
        assert history is not None
        assert history.id == response.json()["history_id"]
        assert history.result == "NO_RECORDED_MATCH_FOUND"
        assert history.medication_name == "Aspirin"


def test_unknown_medication_returns_unable_and_stores_history(
    client: TestClient,
    session_factory: sessionmaker[Session],
) -> None:
    patient_id = create_patient(client)
    app.dependency_overrides[get_rxnorm_service] = lambda: FakeRxNormService(
        error=MedicationNotFoundError()
    )

    response = check(client, patient_id, "Unknown medicine")

    assert response.status_code == 200
    assert response.json()["result"] == "UNABLE_TO_VERIFY"
    assert response.json()["active_ingredients"] == []
    with session_factory() as db:
        history = db.scalar(select(models.SearchHistory))
        assert history is not None
        assert history.result == "UNABLE_TO_VERIFY"


def test_external_api_failure_returns_unable_to_verify(
    client: TestClient,
    session_factory: sessionmaker[Session],
) -> None:
    patient_id = create_patient(client)
    app.dependency_overrides[get_rxnorm_service] = lambda: FakeRxNormService(
        error=RxNormTimeoutError()
    )

    response = check(client, patient_id, "Aspirin")

    assert response.status_code == 200
    assert response.json()["result"] == "UNABLE_TO_VERIFY"
    response_text = response.text.upper()
    assert '"SAFE"' not in response_text
    assert '"APPROVED"' not in response_text
    assert '"RECOMMENDED"' not in response_text
    assert '"APPROPRIATE"' not in response_text

    with session_factory() as db:
        history_rows = list(db.scalars(select(models.SearchHistory)))
        assert len(history_rows) == 1
        assert history_rows[0].result == "UNABLE_TO_VERIFY"
        assert history_rows[0].normalized_medication_name is None
        assert history_rows[0].medication_rxcui is None


def test_incomplete_ingredient_data_without_match_is_unable(client: TestClient) -> None:
    patient_id = create_patient(client)
    set_rxnorm_result(medication_result([], complete=False))

    response = check(client, patient_id)

    assert response.json()["result"] == "UNABLE_TO_VERIFY"


def test_missing_patient_does_not_call_rxnorm_or_store_history(
    client: TestClient,
    session_factory: sessionmaker[Session],
) -> None:
    user = create_authenticated_user(client, "screening.missing@example.com")
    client.headers.update(user["headers"])
    called = False

    class TrackingService:
        def search_medication(self, drug_name: str):
            nonlocal called
            called = True

    app.dependency_overrides[get_rxnorm_service] = TrackingService

    response = check(client, 999)

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "PATIENT_NOT_FOUND"
    assert called is False
    with session_factory() as db:
        assert list(db.scalars(select(models.SearchHistory))) == []
