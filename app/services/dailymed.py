import re
from typing import Any

import httpx

from app import schemas


DAILYMED_BASE_URL = "https://dailymed.nlm.nih.gov"
DAILYMED_TIMEOUT_SECONDS = 5.0
DAILYMED_LABEL_PATH = "/dailymed/services/v2/spls.json"
DAILYMED_LABEL_URL = "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid="
SET_ID_PATTERN = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


class DailyMedTimeoutError(Exception):
    """Raised when DailyMed does not respond before the timeout."""


class DailyMedUnavailableError(Exception):
    """Raised when DailyMed cannot be reached or returns an HTTP error."""


class IncompleteDailyMedResponseError(Exception):
    """Raised when the top-level DailyMed response is malformed."""


class DailyMedService:
    def __init__(self, client: httpx.Client) -> None:
        self.client = client

    def find_labels(
        self,
        rxcui: str,
        limit: int = 5,
    ) -> tuple[list[schemas.DailyMedLabelReference], bool]:
        """Return recent label references associated with an RxNorm concept."""
        data = self._get_json(
            DAILYMED_LABEL_PATH,
            params={
                "rxcui": rxcui,
                "pagesize": str(limit),
                "page": "1",
            },
        )
        records = data.get("data")
        if not isinstance(records, list):
            raise IncompleteDailyMedResponseError

        labels: list[schemas.DailyMedLabelReference] = []
        seen_set_ids: set[str] = set()
        complete = True
        for record in records:
            label = self._parse_label(record)
            if label is None:
                complete = False
                continue
            if label.set_id in seen_set_ids:
                continue
            seen_set_ids.add(label.set_id)
            labels.append(label)
            if len(labels) == limit:
                break
        return labels, complete

    def _get_json(
        self,
        path: str,
        params: dict[str, str],
    ) -> dict[str, Any]:
        try:
            response = self.client.get(path, params=params)
            response.raise_for_status()
        except httpx.TimeoutException as error:
            raise DailyMedTimeoutError from error
        except httpx.HTTPError as error:
            raise DailyMedUnavailableError from error

        try:
            data = response.json()
        except ValueError as error:
            raise IncompleteDailyMedResponseError from error
        if not isinstance(data, dict):
            raise IncompleteDailyMedResponseError
        return data

    @staticmethod
    def _parse_label(record: object) -> schemas.DailyMedLabelReference | None:
        if not isinstance(record, dict):
            return None
        set_id = record.get("setid")
        title = record.get("title")
        published_date = record.get("published_date")
        version = record.get("spl_version")
        if not (
            isinstance(set_id, str)
            and SET_ID_PATTERN.fullmatch(set_id.strip())
            and isinstance(title, str)
            and title.strip()
            and len(title.strip()) <= 1000
            and isinstance(published_date, str)
            and published_date.strip()
            and isinstance(version, (str, int))
            and str(version).strip()
        ):
            return None

        clean_set_id = set_id.strip().lower()
        return schemas.DailyMedLabelReference(
            set_id=clean_set_id,
            title=title.strip(),
            published_date=published_date.strip(),
            version=str(version).strip(),
            url=f"{DAILYMED_LABEL_URL}{clean_set_id}",
        )
