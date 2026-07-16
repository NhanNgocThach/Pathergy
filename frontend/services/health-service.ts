import { apiRequest } from "@/lib/api-client";
import type { AllergyValues, MedicationValues, PatientValues } from "@/schemas/health";
import type { Allergy, MedicationCheckResult, MedicationDetailsResult, MedicationSearchResult, MedicationSuggestionsResult, Patient, ScreeningHistory } from "@/types/health";

export const patientService = {
  list: () => apiRequest<Patient[]>("/patients"),
  get: (patientId: number) => apiRequest<Patient>(`/patients/${patientId}`),
  update: (patientId: number, values: PatientValues) => apiRequest<Patient>(`/patients/${patientId}`, { method: "PUT", json: values }),
};
export const allergyService = {
  list: (patientId: number) => apiRequest<Allergy[]>(`/patients/${patientId}/allergies`),
  get: (patientId: number, allergyId: number) => apiRequest<Allergy>(`/patients/${patientId}/allergies/${allergyId}`),
  create: (patientId: number, values: AllergyValues) => apiRequest<Allergy>(`/patients/${patientId}/allergies`, { method: "POST", json: { ...values, rxcui: values.rxcui || null, reaction: values.reaction || null } }),
  update: (patientId: number, allergyId: number, values: AllergyValues) => apiRequest<Allergy>(`/patients/${patientId}/allergies/${allergyId}`, { method: "PUT", json: { ...values, rxcui: values.rxcui || null, reaction: values.reaction || null } }),
  remove: (patientId: number, allergyId: number) => apiRequest<void>(`/patients/${patientId}/allergies/${allergyId}`, { method: "DELETE" }),
};
export const medicationService = {
  suggestions: (query: string, signal?: AbortSignal) => apiRequest<MedicationSuggestionsResult>(`/medications/suggestions?q=${encodeURIComponent(query)}&limit=8`, { auth: false, signal }),
  search: (name: string) => apiRequest<MedicationSearchResult>(`/medications/search?name=${encodeURIComponent(name)}`, { auth: false }),
  details: (name: string) => apiRequest<MedicationDetailsResult>(`/medications/details?name=${encodeURIComponent(name)}`, { auth: false }),
  check: (patientId: number, values: MedicationValues) => apiRequest<MedicationCheckResult>(`/patients/${patientId}/medication-check`, { method: "POST", json: values }),
};
export const historyService = { list: (patientId: number) => apiRequest<ScreeningHistory[]>(`/patients/${patientId}/screening-history`) };
