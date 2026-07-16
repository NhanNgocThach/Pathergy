export type Patient = { id: number; first_name: string; last_name: string; date_of_birth: string };
export type Severity = "mild" | "moderate" | "severe";
export type Allergy = { id: number; patient_id: number; substance: string; rxcui: string | null; reaction: string | null; severity: Severity };
export type MedicationIngredient = { rxcui: string; name: string };
export type MedicationSearchResult = { query: string; normalized_name: string; rxcui: string; active_ingredients: MedicationIngredient[]; ingredient_data_complete: boolean; disclaimer: string };
export type DailyMedStatus = "AVAILABLE" | "NOT_FOUND" | "UNAVAILABLE" | "INCOMPLETE";
export type DailyMedLabelReference = { set_id: string; title: string; published_date: string; version: string; url: string };
export type MedicationDetailsResult = MedicationSearchResult & {
  dailymed: {
    status: DailyMedStatus;
    labels: DailyMedLabelReference[];
    message: string;
    disclaimer: string;
  };
};
export type MedicationSuggestion = { rxcui: string; name: string; rank: number };
export type MedicationSuggestionsResult = {
  success: boolean;
  data: { query: string; suggestions: MedicationSuggestion[] };
  message: string;
};
export type MedicationCheckStatus = "POTENTIAL_ALLERGY_MATCH" | "NO_RECORDED_MATCH_FOUND" | "UNABLE_TO_VERIFY";
export type AllergyMatch = { allergy_id: number; recorded_substance: string; recorded_rxcui: string | null; ingredient_name: string; ingredient_rxcui: string; match_method: "RXCUI" | "NORMALIZED_TEXT" };
export type MedicationCheckResult = { history_id: number; patient_id: number; medication_query: string; normalized_medication_name: string | null; medication_rxcui: string | null; active_ingredients: MedicationIngredient[]; result: MedicationCheckStatus; matches: AllergyMatch[]; message: string; disclaimer: string };
export type ScreeningHistory = { id: number; patient_id: number; medication_name: string; normalized_medication_name: string | null; medication_rxcui: string | null; result: MedicationCheckStatus; created_at: string };
