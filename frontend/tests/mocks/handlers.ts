import { http, HttpResponse } from "msw";

export const API_URL = "http://api.test";

export const currentUser = {
  user_id: 1,
  email: "fictional.user@example.com",
  phone_number_masked: null,
  display_name: "Fictional User",
  patient_id: 10,
  email_verified_at: "2026-01-01T00:00:00Z",
  phone_verified_at: null,
  is_active: true,
};

export const tokenPair = {
  access_token: "access-token",
  refresh_token: "refresh-token",
  token_type: "bearer",
  access_token_expires_in: 900,
  refresh_token_expires_in: 2592000,
};

export const patient = { id: 10, first_name: "Fictional", last_name: "User", date_of_birth: "1990-01-01" };
export const allergies = [{ id: 1, patient_id: 10, substance: "Fictional ingredient", rxcui: "123", reaction: "Fictional rash", severity: "moderate" }];
export const history = [{ id: 7, patient_id: 10, medication_name: "Fictional medicine", normalized_medication_name: "Fictional medicine 10 MG", medication_rxcui: "900", result: "NO_RECORDED_MATCH_FOUND", created_at: "2026-01-03T00:00:00Z" }];
export const familyEntries = [{ family_group: { family_group_id: 5, name: "Fictional Household", created_by_user_id: 1, created_at: "2026-01-01T00:00:00Z", updated_at: "2026-01-01T00:00:00Z", is_active: true }, membership: { membership_id: 50, family_group_id: 5, user_id: 1, role: "OWNER", relationship: "SELF", status: "ACTIVE", joined_at: "2026-01-01T00:00:00Z", left_at: null, created_at: "2026-01-01T00:00:00Z", updated_at: "2026-01-01T00:00:00Z" } }];

export const handlers = [
  http.post(`${API_URL}/auth/login`, () => HttpResponse.json(tokenPair)),
  http.get(`${API_URL}/auth/me`, () => HttpResponse.json(currentUser)),
  http.post(`${API_URL}/auth/register`, () => HttpResponse.json({ user_id: 2, email: "new.user@example.com", patient_id: 20, verification_required: true, verification_url: null }, { status: 201 })),
  http.post(`${API_URL}/auth/verify-email`, () => HttpResponse.json({ message: "Email verified successfully" })),
  http.post(`${API_URL}/auth/forgot-password`, () => HttpResponse.json({ message: "If the account exists, password reset instructions are available.", development_url: null })),
  http.post(`${API_URL}/auth/reset-password`, () => HttpResponse.json({ message: "Password reset successfully; all sessions were revoked" })),
  http.post(`${API_URL}/auth/change-password`, () => HttpResponse.json({ message: "Password changed successfully; all sessions were revoked" })),
  http.post(`${API_URL}/auth/logout`, () => new HttpResponse(null, { status: 204 })),
  http.post(`${API_URL}/auth/refresh`, () => HttpResponse.json(tokenPair)),
  http.get(`${API_URL}/auth/sessions`, () => HttpResponse.json([{ session_id: "session-1", device_name: "Fictional browser", device_type: "browser", ip_address: "127.0.0.1", user_agent: "Pathergy Test Browser", created_at: "2026-01-01T00:00:00Z", last_used_at: "2026-01-02T00:00:00Z", expires_at: "2026-02-01T00:00:00Z", is_current: true }])),
  http.delete(`${API_URL}/auth/sessions/:sessionId`, () => new HttpResponse(null, { status: 204 })),
  http.delete(`${API_URL}/auth/sessions`, () => new HttpResponse(null, { status: 204 })),
  http.get(`${API_URL}/patients`, () => HttpResponse.json([patient])),
  http.get(`${API_URL}/patients/:patientId`, () => HttpResponse.json(patient)),
  http.put(`${API_URL}/patients/:patientId`, async ({ request }) => HttpResponse.json({ id: 10, ...await request.json() as object })),
  http.get(`${API_URL}/patients/:patientId/allergies`, () => HttpResponse.json(allergies)),
  http.get(`${API_URL}/patients/:patientId/allergies/:allergyId`, () => HttpResponse.json(allergies[0])),
  http.post(`${API_URL}/patients/:patientId/allergies`, async ({ request }) => HttpResponse.json({ id: 2, patient_id: 10, ...await request.json() as object }, { status: 201 })),
  http.put(`${API_URL}/patients/:patientId/allergies/:allergyId`, async ({ request }) => HttpResponse.json({ id: 1, patient_id: 10, ...await request.json() as object })),
  http.delete(`${API_URL}/patients/:patientId/allergies/:allergyId`, () => new HttpResponse(null, { status: 204 })),
  http.get(`${API_URL}/medications/suggestions`, ({ request }) => {
    const query = new URL(request.url).searchParams.get("q") ?? "";
    return HttpResponse.json({
      success: true,
      data: {
        query,
        suggestions: [
          { rxcui: "900", name: "Fictional medicine", rank: 1 },
          { rxcui: "901", name: "Fictional medicine extended release", rank: 2 },
        ],
      },
      message: "Medication suggestions retrieved successfully.",
    });
  }),
  http.get(`${API_URL}/medications/search`, () => HttpResponse.json({ query: "Fictional medicine", normalized_name: "Fictional medicine 10 MG", rxcui: "900", active_ingredients: [{ rxcui: "123", name: "Fictional ingredient" }, { rxcui: "124", name: "Second fictional ingredient" }], ingredient_data_complete: true, disclaimer: "RxNorm data identifies concepts and ingredients only." })),
  http.get(`${API_URL}/medications/details`, () => HttpResponse.json({ query: "Fictional medicine", normalized_name: "Fictional medicine 10 MG", rxcui: "900", active_ingredients: [{ rxcui: "123", name: "Fictional ingredient" }, { rxcui: "124", name: "Second fictional ingredient" }], ingredient_data_complete: true, disclaimer: "RxNorm data identifies medication concepts and ingredients only.", dailymed: { status: "AVAILABLE", labels: [{ set_id: "11111111-2222-3333-4444-555555555555", title: "FICTIONAL MEDICINE OFFICIAL LABEL", published_date: "Jul 10, 2026", version: "3", url: "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=11111111-2222-3333-4444-555555555555" }], message: "DailyMed label references retrieved.", disclaimer: "DailyMed links are official U.S. label references associated with the RxCUI. Labels may represent different products and do not provide medical advice." } })),
  http.post(`${API_URL}/patients/:patientId/medication-check`, () => HttpResponse.json({ history_id: 8, patient_id: 10, medication_query: "Fictional medicine", normalized_medication_name: "Fictional medicine 10 MG", medication_rxcui: "900", active_ingredients: [{ rxcui: "123", name: "Fictional ingredient" }], result: "POTENTIAL_ALLERGY_MATCH", matches: [{ allergy_id: 1, recorded_substance: "Fictional ingredient", recorded_rxcui: "123", ingredient_name: "Fictional ingredient", ingredient_rxcui: "123", match_method: "RXCUI" }], message: "One or more recorded allergies match.", disclaimer: "Educational prototype only. This result is not medical advice." })),
  http.get(`${API_URL}/patients/:patientId/screening-history`, () => HttpResponse.json(history)),
  http.get(`${API_URL}/users/:userId/family-groups`, () => HttpResponse.json(familyEntries)),
  http.get(`${API_URL}/family-groups/:groupId`, () => HttpResponse.json(familyEntries[0].family_group)),
  http.post(`${API_URL}/family-groups`, async ({ request }) => HttpResponse.json({ family_group_id: 6, created_by_user_id: 1, created_at: "2026-01-01T00:00:00Z", updated_at: "2026-01-01T00:00:00Z", is_active: true, ...await request.json() as object }, { status: 201 })),
  http.put(`${API_URL}/family-groups/:groupId`, async ({ request }) => HttpResponse.json({ ...familyEntries[0].family_group, ...await request.json() as object })),
  http.get(`${API_URL}/family-groups/:groupId/members`, () => HttpResponse.json([familyEntries[0].membership, { membership_id: 51, family_group_id: 5, user_id: 2, role: "MEMBER", relationship: "RELATIVE", status: "PENDING", joined_at: null, left_at: null, created_at: "2026-01-02T00:00:00Z", updated_at: "2026-01-02T00:00:00Z" }])),
  http.post(`${API_URL}/family-groups/:groupId/members`, async ({ request }) => HttpResponse.json({ membership_id: 52, family_group_id: 5, status: "PENDING", joined_at: null, left_at: null, created_at: "2026-01-02T00:00:00Z", updated_at: "2026-01-02T00:00:00Z", ...await request.json() as object }, { status: 201 })),
  http.put(`${API_URL}/family-groups/:groupId/members/:userId`, async ({ request }) => HttpResponse.json({ ...familyEntries[0].membership, ...await request.json() as object })),
  http.delete(`${API_URL}/family-groups/:groupId/members/:userId`, () => HttpResponse.json({ ...familyEntries[0].membership, status: "REMOVED" })),
  http.post(`${API_URL}/family-groups/:groupId/members/:userId/leave`, () => HttpResponse.json({ ...familyEntries[0].membership, status: "LEFT" })),
  http.get(`${API_URL}/family-groups/:groupId/members/:userId/permissions`, () => HttpResponse.json(["BASIC_PROFILE", "ALLERGIES", "SCREENING_HISTORY"].map((data_type, index) => ({ permission_id: index + 1, membership_id: 50, data_type, can_view: false, can_edit: false, created_at: "2026-01-01T00:00:00Z", updated_at: "2026-01-01T00:00:00Z" })))),
  http.put(`${API_URL}/family-groups/:groupId/members/:userId/permissions`, async ({ request }) => { const body = await request.json() as { permissions: object[] }; return HttpResponse.json(body.permissions.map((permission, index) => ({ permission_id: index + 1, membership_id: 50, created_at: "2026-01-01T00:00:00Z", updated_at: "2026-01-01T00:00:00Z", ...permission }))); }),
];
