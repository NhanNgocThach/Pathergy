from datetime import date
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Severity(str, Enum):
    mild = "mild"
    moderate = "moderate"
    severe = "severe"


class PatientData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    first_name: str = Field(min_length=1, max_length=50, examples=["Jamie"])
    last_name: str = Field(min_length=1, max_length=50, examples=["Rivera"])
    date_of_birth: date = Field(examples=["1994-06-15"])

    @field_validator("first_name", "last_name", mode="before")
    @classmethod
    def strip_names(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("date_of_birth")
    @classmethod
    def reject_future_birth_date(cls, value: date) -> date:
        if value > date.today():
            raise ValueError("date of birth cannot be in the future")
        return value


class PatientCreate(PatientData):
    pass


class PatientUpdate(PatientData):
    pass


class PatientResponse(PatientData):
    model_config = ConfigDict(from_attributes=True)

    id: int


class AllergyData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    substance: str = Field(min_length=2, max_length=100, examples=["Penicillin"])
    rxcui: str | None = Field(
        default=None,
        min_length=1,
        max_length=20,
        pattern=r"^\d+$",
        description="Optional RxNorm identifier for the recorded substance",
        examples=["7980"],
    )
    reaction: str | None = Field(
        default=None,
        min_length=2,
        max_length=200,
        examples=["Fictional example: skin rash"],
    )
    severity: Severity = Field(examples=["moderate"])

    @field_validator("substance", "rxcui", mode="before")
    @classmethod
    def strip_allergy_identifiers(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value

    @field_validator("reaction", mode="before")
    @classmethod
    def strip_reaction(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class AllergyCreate(AllergyData):
    pass


class AllergyUpdate(AllergyData):
    pass


class AllergyResponse(AllergyData):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int


class MedicationIngredient(BaseModel):
    rxcui: str = Field(description="RxNorm concept identifier for the ingredient")
    name: str = Field(description="Standardized RxNorm ingredient name")


class MedicationSearchResponse(BaseModel):
    query: str
    normalized_name: str
    rxcui: str = Field(description="RxNorm concept identifier for the medication")
    active_ingredients: list[MedicationIngredient]
    ingredient_data_complete: bool
    disclaimer: str = (
        "RxNorm data identifies medication concepts and ingredients only. "
        "This response does not determine whether a medication is safe."
    )


class MedicationCheckResult(str, Enum):
    potential_allergy_match = "POTENTIAL_ALLERGY_MATCH"
    no_recorded_match_found = "NO_RECORDED_MATCH_FOUND"
    unable_to_verify = "UNABLE_TO_VERIFY"


class MatchMethod(str, Enum):
    rxcui = "RXCUI"
    normalized_text = "NORMALIZED_TEXT"


class MedicationCheckRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    medication_name: str = Field(
        min_length=2,
        max_length=100,
        examples=["Augmentin"],
    )

    @field_validator("medication_name", mode="before")
    @classmethod
    def strip_medication_name(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class AllergyMatch(BaseModel):
    allergy_id: int
    recorded_substance: str
    recorded_rxcui: str | None
    ingredient_name: str
    ingredient_rxcui: str
    match_method: MatchMethod


class MedicationCheckResponse(BaseModel):
    history_id: int
    patient_id: int
    medication_query: str
    normalized_medication_name: str | None
    medication_rxcui: str | None
    active_ingredients: list[MedicationIngredient]
    result: MedicationCheckResult
    matches: list[AllergyMatch]
    message: str
    disclaimer: str = (
        "Educational prototype only. This result is not medical advice. "
        "Consult a qualified healthcare professional."
    )
