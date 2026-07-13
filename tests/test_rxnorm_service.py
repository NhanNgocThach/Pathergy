import httpx
import pytest

from app.services.rxnorm import (
    RXNORM_BASE_URL,
    IncompleteRxNormResponseError,
    MedicationNotFoundError,
    RxNormService,
    RxNormTimeoutError,
    RxNormUnavailableError,
)


def make_service(handler) -> RxNormService:
    transport = httpx.MockTransport(handler)
    client = httpx.Client(base_url=RXNORM_BASE_URL, transport=transport)
    return RxNormService(client)


def test_search_returns_normalized_medication_and_ingredients() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/REST/rxcui.json":
            assert request.url.params["name"] == "Augmentin"
            assert request.url.params["search"] == "2"
            return httpx.Response(
                200,
                json={"idGroup": {"rxnormId": ["19711"]}},
            )
        if request.url.path == "/REST/rxcui/19711/properties.json":
            return httpx.Response(
                200,
                json={
                    "properties": {
                        "rxcui": "19711",
                        "name": "amoxicillin / clavulanate potassium",
                        "tty": "MIN",
                    }
                },
            )
        return httpx.Response(
            200,
            json={
                "relatedGroup": {
                    "conceptGroup": [
                        {
                            "tty": "IN",
                            "conceptProperties": [
                                {"rxcui": "723", "name": "amoxicillin"},
                                {
                                    "rxcui": "21212",
                                    "name": "clavulanate potassium",
                                },
                            ],
                        }
                    ]
                }
            },
        )

    result = make_service(handler).search_medication("Augmentin")

    assert result.normalized_name == "amoxicillin / clavulanate potassium"
    assert result.rxcui == "19711"
    assert [ingredient.name for ingredient in result.active_ingredients] == [
        "amoxicillin",
        "clavulanate potassium",
    ]
    assert result.ingredient_data_complete is True
    assert "safe" in result.disclaimer.lower()


def test_ingredient_concept_returns_itself_as_ingredient() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/REST/rxcui.json":
            return httpx.Response(200, json={"idGroup": {"rxnormId": ["1191"]}})
        if request.url.path.endswith("properties.json"):
            return httpx.Response(
                200,
                json={
                    "properties": {
                        "rxcui": "1191",
                        "name": "aspirin",
                        "tty": "IN",
                    }
                },
            )
        return httpx.Response(200, json={})

    result = make_service(handler).search_medication("aspirin")

    assert result.active_ingredients[0].name == "aspirin"
    assert result.ingredient_data_complete is True


def test_no_match_raises_not_found() -> None:
    service = make_service(
        lambda request: httpx.Response(200, json={"idGroup": {}})
    )

    with pytest.raises(MedicationNotFoundError):
        service.search_medication("not-a-real-medication")


def test_timeout_is_translated() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out", request=request)

    with pytest.raises(RxNormTimeoutError):
        make_service(handler).search_medication("aspirin")


def test_upstream_http_error_is_translated() -> None:
    service = make_service(lambda request: httpx.Response(503))

    with pytest.raises(RxNormUnavailableError):
        service.search_medication("aspirin")


def test_missing_required_properties_is_incomplete() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/REST/rxcui.json":
            return httpx.Response(200, json={"idGroup": {"rxnormId": ["1191"]}})
        return httpx.Response(
            200,
            json={"properties": {"rxcui": "1191", "tty": "IN"}},
        )

    with pytest.raises(IncompleteRxNormResponseError):
        make_service(handler).search_medication("aspirin")


def test_missing_ingredient_group_returns_clear_incomplete_state() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/REST/rxcui.json":
            return httpx.Response(200, json={"idGroup": {"rxnormId": ["123"]}})
        if request.url.path.endswith("properties.json"):
            return httpx.Response(
                200,
                json={
                    "properties": {
                        "rxcui": "123",
                        "name": "Example normalized medication",
                        "tty": "SCD",
                    }
                },
            )
        return httpx.Response(200, json={})

    result = make_service(handler).search_medication("Example medication")

    assert result.active_ingredients == []
    assert result.ingredient_data_complete is False
