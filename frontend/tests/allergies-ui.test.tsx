import { http, HttpResponse } from "msw";
import { describe, expect, it } from "vitest";
import { AllergyCreate, AllergyEdit } from "@/features/allergies/allergy-form";
import { AllergyList } from "@/features/allergies/allergy-list";
import { API_URL } from "@/tests/mocks/handlers";
import { server } from "@/tests/mocks/server";
import { renderWithProfile, screen, userEvent } from "@/tests/test-utils";

describe("allergy management", () => {
  it("lists allergy details with severity words", async () => { renderWithProfile(<AllergyList />); expect(await screen.findAllByText("Fictional ingredient")).not.toHaveLength(0); expect(screen.getAllByText("Moderate")[0]).toBeVisible(); });
  it("adds an allergy record", async () => { const user = userEvent.setup(); renderWithProfile(<AllergyCreate />); await user.type(screen.getByLabelText("Substance"), "Another fictional ingredient"); await user.selectOptions(screen.getByLabelText("Severity"), "mild"); await user.click(screen.getByRole("button", { name: "Add allergy record" })); expect(screen.queryByText("Allergy record was not saved")).not.toBeInTheDocument(); });
  it("shows the duplicate backend conflict", async () => { server.use(http.post(`${API_URL}/patients/10/allergies`, () => HttpResponse.json({ detail: "This patient already has an allergy record for that substance" }, { status: 409 }))); const user = userEvent.setup(); renderWithProfile(<AllergyCreate />); await user.type(screen.getByLabelText("Substance"), "Fictional ingredient"); await user.click(screen.getByRole("button", { name: "Add allergy record" })); expect(await screen.findByText("This patient already has an allergy record for that substance")).toBeVisible(); });
  it("loads an allergy for editing", async () => { renderWithProfile(<AllergyEdit allergyId={1} />); expect(await screen.findByDisplayValue("Fictional ingredient")).toBeVisible(); });
  it("requires confirmation before deleting", async () => { const user = userEvent.setup(); renderWithProfile(<AllergyList />); const buttons = await screen.findAllByRole("button", { name: "Delete Fictional ingredient" }); await user.click(buttons[0]); expect(screen.getByRole("heading", { name: "Delete allergy record?" })).toBeVisible(); expect(screen.getByRole("button", { name: "Delete record" })).toBeVisible(); });
  it("renders permission denial without health rows", async () => { server.use(http.get(`${API_URL}/patients/10/allergies`, () => HttpResponse.json({ detail: { code: "FAMILY_PERMISSION_DENIED", message: "Denied" } }, { status: 403 }))); renderWithProfile(<AllergyList />); expect(await screen.findByRole("heading", { name: "Permission required" })).toBeVisible(); expect(screen.queryByText("Fictional rash")).not.toBeInTheDocument(); });
});
