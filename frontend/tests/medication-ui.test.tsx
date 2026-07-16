import { http, HttpResponse } from "msw";
import { describe, expect, it } from "vitest";
import { MedicationCheck } from "@/features/medications/medication-check";
import { MedicationResultPanel } from "@/features/medications/medication-result-panel";
import { API_URL } from "@/tests/mocks/handlers";
import { server } from "@/tests/mocks/server";
import { renderWithProfile, screen, userEvent } from "@/tests/test-utils";
import type { MedicationCheckResult } from "@/types/health";

const base: MedicationCheckResult = { history_id: 8, patient_id: 10, medication_query: "Fictional medicine", normalized_medication_name: "Fictional medicine 10 MG", medication_rxcui: "900", active_ingredients: [{ rxcui: "123", name: "Fictional ingredient" }], result: "POTENTIAL_ALLERGY_MATCH", matches: [{ allergy_id: 1, recorded_substance: "Fictional ingredient", recorded_rxcui: "123", ingredient_name: "Fictional ingredient", ingredient_rxcui: "123", match_method: "RXCUI" }], message: "Match", disclaimer: "Educational prototype only. This result is not medical advice." };

describe("medication screening", () => {
  it("suggests RxNorm medication names while typing", async () => {
    const user = userEvent.setup();
    renderWithProfile(<MedicationCheck />);

    await user.type(screen.getByLabelText("Medication name"), "Fic");

    expect(await screen.findByRole("option", { name: /Fictional medicine, RxCUI 900/ })).toBeVisible();
  });
  it("shows RxNorm ingredients and linked DailyMed labels", async () => {
    const user = userEvent.setup();
    renderWithProfile(<MedicationCheck />);

    await user.type(screen.getByLabelText("Medication name"), "Fictional medicine");
    await user.click(screen.getByRole("button", { name: "View medication details" }));

    expect(await screen.findByText("Fictional medicine 10 MG")).toBeVisible();
    expect(screen.getByText(/Second fictional ingredient/)).toBeVisible();
    const label = screen.getByRole("link", { name: /FICTIONAL MEDICINE OFFICIAL LABEL/ });
    expect(label).toHaveAttribute("href", "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=11111111-2222-3333-4444-555555555555");
    expect(label).toHaveAttribute("target", "_blank");
  });
  it("keeps autocomplete suggestions when medication details are enabled", async () => {
    const user = userEvent.setup();
    renderWithProfile(<MedicationCheck />);
    const input = screen.getByRole("combobox", { name: "Medication name" });

    await user.type(input, "Fic");
    await user.click(await screen.findByRole("option", { name: /Fictional medicine, RxCUI 900/ }));
    expect(input).toHaveValue("Fictional medicine");
    await user.click(screen.getByRole("button", { name: "View medication details" }));

    expect(await screen.findByText("Official DailyMed labels")).toBeVisible();
  });
  it("shows a non-blocking DailyMed unavailable state with RxNorm data", async () => {
    server.use(http.get(`${API_URL}/medications/details`, () => HttpResponse.json({ query: "Fictional medicine", normalized_name: "Fictional medicine 10 MG", rxcui: "900", active_ingredients: [{ rxcui: "123", name: "Fictional ingredient" }], ingredient_data_complete: true, disclaimer: "RxNorm data identifies concepts only.", dailymed: { status: "UNAVAILABLE", labels: [], message: "DailyMed is currently unavailable.", disclaimer: "Official label links only." } })));
    const user = userEvent.setup();
    renderWithProfile(<MedicationCheck />);

    await user.type(screen.getByLabelText("Medication name"), "Fictional medicine");
    await user.click(screen.getByRole("button", { name: "View medication details" }));

    expect(await screen.findByText("Fictional medicine 10 MG")).toBeVisible();
    expect(screen.getByText("DailyMed temporarily unavailable")).toBeVisible();
    expect(screen.getByText("DailyMed is currently unavailable. Confirmed RxNorm information is still shown.")).toBeVisible();
  });
  it("renders a potential match with recorded and ingredient data", () => { renderWithProfile(<MedicationResultPanel result={base} />); expect(screen.getByRole("heading", { name: "Potential allergy match" })).toBeVisible(); expect(screen.getByText("Review this result with a qualified healthcare professional.")).toBeVisible(); });
  it("renders a neutral no-recorded-match result without prohibited claims", () => { renderWithProfile(<MedicationResultPanel result={{ ...base, result: "NO_RECORDED_MATCH_FOUND", matches: [] }} />); expect(screen.getByRole("heading", { name: "No recorded match found" })).toBeVisible(); expect(screen.queryByText(/\bsafe\b/i)).not.toBeInTheDocument(); expect(screen.queryByText(/\bapproved\b|\bsuitable\b|\bno risk\b/i)).not.toBeInTheDocument(); });
  it("renders unable-to-verify as a completed conservative result", () => { renderWithProfile(<MedicationResultPanel result={{ ...base, result: "UNABLE_TO_VERIFY", matches: [], active_ingredients: [] }} />); expect(screen.getByRole("heading", { name: "Unable to verify" })).toBeVisible(); expect(screen.getByText(/No medical conclusion can be made/)).toBeVisible(); });
  it("shows an RxNorm timeout without a medical conclusion", async () => { server.use(http.get(`${API_URL}/medications/details`, () => HttpResponse.json({ detail: "RxNorm did not respond before the timeout" }, { status: 504 }))); const user = userEvent.setup(); renderWithProfile(<MedicationCheck />); await user.type(screen.getByLabelText("Medication name"), "Fictional medicine"); await user.click(screen.getByRole("button", { name: "View medication details" })); expect(await screen.findByText("RxNorm did not respond before the timeout")).toBeVisible(); });
});
