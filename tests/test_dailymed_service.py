import httpx
import pytest

from app.services.dailymed import (
    DAILYMED_BASE_URL,
    DAILYMED_LABEL_PATH,
    DailyMedService,
    DailyMedTimeoutError,
    DailyMedUnavailableError,
    IncompleteDailyMedResponseError,
)


def make_service(handler) -> DailyMedService:
    transport = httpx.MockTransport(handler)
    client = httpx.Client(base_url=DAILYMED_BASE_URL, transport=transport)
    return DailyMedService(client)


def test_find_labels_returns_structured_deduplicated_references() -> None:
    set_id = "ce58105b-f010-47af-8f31-6dd4ce4e9cba"

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == DAILYMED_LABEL_PATH
        assert request.url.params["rxcui"] == "220581"
        assert request.url.params["pagesize"] == "5"
        assert request.url.params["page"] == "1"
        return httpx.Response(
            200,
            json={
                "data": [
                    {
                        "setid": set_id.upper(),
                        "title": " TYLENOL PM FICTIONAL LABEL ",
                        "published_date": "Jun 10, 2026",
                        "spl_version": 14,
                    },
                    {
                        "setid": set_id,
                        "title": "Duplicate",
                        "published_date": "Jun 10, 2026",
                        "spl_version": "14",
                    },
                ]
            },
        )

    labels, complete = make_service(handler).find_labels("220581")

    assert complete is True
    assert len(labels) == 1
    assert labels[0].model_dump() == {
        "set_id": set_id,
        "title": "TYLENOL PM FICTIONAL LABEL",
        "published_date": "Jun 10, 2026",
        "version": "14",
        "url": (
            "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid="
            f"{set_id}"
        ),
    }


def test_no_associated_labels_is_a_complete_empty_result() -> None:
    service = make_service(lambda request: httpx.Response(200, json={"data": []}))

    labels, complete = service.find_labels("999999")

    assert labels == []
    assert complete is True


def test_malformed_label_is_skipped_and_marks_data_incomplete() -> None:
    service = make_service(
        lambda request: httpx.Response(
            200,
            json={
                "data": [
                    {
                        "setid": "not-a-safe-set-id",
                        "title": "Invalid label",
                        "published_date": "Jun 10, 2026",
                        "spl_version": "1",
                    }
                ]
            },
        )
    )

    labels, complete = service.find_labels("161")

    assert labels == []
    assert complete is False


def test_valid_labels_are_preserved_when_another_record_is_incomplete() -> None:
    service = make_service(
        lambda request: httpx.Response(
            200,
            json={
                "data": [
                    {
                        "setid": "11111111-2222-3333-4444-555555555555",
                        "title": "FICTIONAL COMPLETE LABEL",
                        "published_date": "Jul 10, 2026",
                        "spl_version": "2",
                    },
                    {"setid": "missing-required-fields"},
                ]
            },
        )
    )

    labels, complete = service.find_labels("161")

    assert [label.title for label in labels] == ["FICTIONAL COMPLETE LABEL"]
    assert complete is False


def test_missing_data_list_is_incomplete() -> None:
    service = make_service(lambda request: httpx.Response(200, json={}))

    with pytest.raises(IncompleteDailyMedResponseError):
        service.find_labels("161")


def test_timeout_is_translated() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out", request=request)

    with pytest.raises(DailyMedTimeoutError):
        make_service(handler).find_labels("161")


def test_http_and_json_errors_are_translated() -> None:
    with pytest.raises(DailyMedUnavailableError):
        make_service(lambda request: httpx.Response(503)).find_labels("161")

    with pytest.raises(IncompleteDailyMedResponseError):
        make_service(
            lambda request: httpx.Response(200, content=b"not-json")
        ).find_labels("161")
