export const queryKeys = {
  patients: ["patients"] as const,
  patient: (patientId: number) => ["patient-data", patientId, "profile"] as const,
  allergies: (patientId: number) => ["patient-data", patientId, "allergies"] as const,
  allergy: (patientId: number, allergyId: number) => ["patient-data", patientId, "allergies", allergyId] as const,
  history: (patientId: number) => ["patient-data", patientId, "history"] as const,
  medicationResult: (historyId: number) => ["medication-result", historyId] as const,
  medicationSuggestions: (query: string) => ["medication-suggestions", query] as const,
  families: (userId: number) => ["families", userId] as const,
  family: (groupId: number) => ["family", groupId] as const,
  members: (groupId: number) => ["family", groupId, "members"] as const,
  permissions: (groupId: number, userId: number) => ["family", groupId, "permissions", userId] as const,
  sessions: ["auth-sessions"] as const,
};
