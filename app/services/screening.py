import unicodedata

from app import models, schemas


def normalize_text(value: str) -> str:
    """Normalize case, Unicode, punctuation, and whitespace without fuzzy matching."""
    normalized = unicodedata.normalize("NFKC", value).casefold()
    words = "".join(character if character.isalnum() else " " for character in normalized)
    return " ".join(words.split())


def find_allergy_matches(
    allergies: list[models.Allergy],
    ingredients: list[schemas.MedicationIngredient],
) -> list[schemas.AllergyMatch]:
    """Match identifiers first; use exact normalized text only when no ID exists."""
    matches: list[schemas.AllergyMatch] = []

    for allergy in allergies:
        for ingredient in ingredients:
            if allergy.rxcui is not None:
                if allergy.rxcui == ingredient.rxcui:
                    matches.append(
                        build_match(allergy, ingredient, schemas.MatchMethod.rxcui)
                    )
                    break
                continue

            if normalize_text(allergy.substance) == normalize_text(ingredient.name):
                matches.append(
                    build_match(
                        allergy,
                        ingredient,
                        schemas.MatchMethod.normalized_text,
                    )
                )
                break

    return matches


def build_match(
    allergy: models.Allergy,
    ingredient: schemas.MedicationIngredient,
    method: schemas.MatchMethod,
) -> schemas.AllergyMatch:
    return schemas.AllergyMatch(
        allergy_id=allergy.id,
        recorded_substance=allergy.substance,
        recorded_rxcui=allergy.rxcui,
        ingredient_name=ingredient.name,
        ingredient_rxcui=ingredient.rxcui,
        match_method=method,
    )
