from typing import Any

import httpx

from app import schemas

RXNORM_BASE_URL = "https://rxnav.nlm.nih.gov"
RXNORM_TIMEOUT_SECONDS = 5.0


class MedicationNotFoundError(Exception):
    """Raised when RxNorm has no exact or normalized match."""


class RxNormTimeoutError(Exception):
    """Raised when RxNorm does not respond before the timeout."""


class RxNormUnavailableError(Exception):
    """Raised when RxNorm cannot be reached or returns an HTTP error."""


class IncompleteRxNormResponseError(Exception):
    """Raised when a required RxNorm response field is malformed or missing."""


class RxNormService:
    def __init__(self, client: httpx.Client) -> None:
        self.client = client

    def search_medication(self, drug_name: str) -> schemas.MedicationSearchResponse:
        """Find a normalized RxNorm concept and its active ingredients."""
        search_data = self._get_json(
            "/REST/rxcui.json",
            params={"name": drug_name, "search": "2", "allsrc": "0"},
        )
        rxcui = self._first_rxcui(search_data)

        properties_data = self._get_json(f"/REST/rxcui/{rxcui}/properties.json")
        properties = self._concept_properties(properties_data)

        related_data = self._get_json(
            f"/REST/rxcui/{rxcui}/related.json",
            params={"tty": "IN"},
        )
        ingredients, ingredient_data_complete = self._ingredients(
            related_data,
            properties,
        )

        return schemas.MedicationSearchResponse(
            query=drug_name,
            normalized_name=properties["name"],
            rxcui=properties["rxcui"],
            active_ingredients=ingredients,
            ingredient_data_complete=ingredient_data_complete,
        )

    def _get_json(
        self,
        path: str,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        try:
            response = self.client.get(path, params=params)
            response.raise_for_status()
        except httpx.TimeoutException as error:
            raise RxNormTimeoutError from error
        except httpx.HTTPError as error:
            raise RxNormUnavailableError from error

        try:
            data = response.json()
        except ValueError as error:
            raise IncompleteRxNormResponseError from error

        if not isinstance(data, dict):
            raise IncompleteRxNormResponseError
        return data

    @staticmethod
    def _first_rxcui(data: dict[str, Any]) -> str:
        id_group = data.get("idGroup")
        if id_group is None:
            raise MedicationNotFoundError
        if not isinstance(id_group, dict):
            raise IncompleteRxNormResponseError

        rxcuis = id_group.get("rxnormId")
        if rxcuis is None or rxcuis == []:
            raise MedicationNotFoundError
        if not isinstance(rxcuis, list) or not isinstance(rxcuis[0], str):
            raise IncompleteRxNormResponseError

        rxcui = rxcuis[0].strip()
        if not rxcui:
            raise IncompleteRxNormResponseError
        return rxcui

    @staticmethod
    def _concept_properties(data: dict[str, Any]) -> dict[str, str]:
        properties = data.get("properties")
        if not isinstance(properties, dict):
            raise IncompleteRxNormResponseError

        rxcui = properties.get("rxcui")
        name = properties.get("name")
        tty = properties.get("tty")
        if not all(isinstance(value, str) and value.strip() for value in (rxcui, name, tty)):
            raise IncompleteRxNormResponseError

        return {
            "rxcui": rxcui.strip(),
            "name": name.strip(),
            "tty": tty.strip(),
        }

    @staticmethod
    def _ingredients(
        data: dict[str, Any],
        properties: dict[str, str],
    ) -> tuple[list[schemas.MedicationIngredient], bool]:
        # An RxNorm ingredient concept is already its own standardized ingredient.
        if properties["tty"] == "IN":
            return [
                schemas.MedicationIngredient(
                    rxcui=properties["rxcui"],
                    name=properties["name"],
                )
            ], True

        related_group = data.get("relatedGroup")
        if related_group is None:
            return [], False
        if not isinstance(related_group, dict):
            raise IncompleteRxNormResponseError

        concept_groups = related_group.get("conceptGroup")
        if concept_groups is None:
            return [], False
        if not isinstance(concept_groups, list):
            raise IncompleteRxNormResponseError

        ingredients_by_rxcui: dict[str, schemas.MedicationIngredient] = {}
        complete = True
        for group in concept_groups:
            if not isinstance(group, dict):
                complete = False
                continue
            concepts = group.get("conceptProperties")
            if concepts is None:
                continue
            if not isinstance(concepts, list):
                complete = False
                continue
            for concept in concepts:
                if not isinstance(concept, dict):
                    complete = False
                    continue
                ingredient_rxcui = concept.get("rxcui")
                ingredient_name = concept.get("name")
                if not (
                    isinstance(ingredient_rxcui, str)
                    and ingredient_rxcui.strip()
                    and isinstance(ingredient_name, str)
                    and ingredient_name.strip()
                ):
                    complete = False
                    continue
                ingredient = schemas.MedicationIngredient(
                    rxcui=ingredient_rxcui.strip(),
                    name=ingredient_name.strip(),
                )
                ingredients_by_rxcui[ingredient.rxcui] = ingredient

        ingredients = list(ingredients_by_rxcui.values())
        return ingredients, complete and bool(ingredients)
