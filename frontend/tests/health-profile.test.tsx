import { http, HttpResponse } from "msw";
import { describe, expect, it } from "vitest";
import { ProfileEdit } from "@/features/patients/profile-edit";
import { ProfileView } from "@/features/patients/profile-view";
import { API_URL } from "@/tests/mocks/handlers";
import { server } from "@/tests/mocks/server";
import { renderWithProfile, screen, userEvent, waitFor } from "@/tests/test-utils";

describe("health profile", () => {
  it("loads the selected personal profile", async () => { renderWithProfile(<ProfileView />); expect(await screen.findByRole("heading", { name: "Fictional User" })).toBeVisible(); expect(screen.getByText("My profile")).toBeVisible(); });
  it("edits the supported complete profile payload", async () => { const user = userEvent.setup(); renderWithProfile(<ProfileEdit />); const firstName = await screen.findByLabelText("First name"); await user.clear(firstName); await user.type(firstName, "Updated"); await user.click(screen.getByRole("button", { name: "Save profile" })); await waitFor(() => expect(screen.queryByText("Profile was not updated")).not.toBeInTheDocument()); });
  it("does not disclose an inaccessible profile", async () => { server.use(http.get(`${API_URL}/patients/10`, () => HttpResponse.json({ detail: { code: "PATIENT_ACCESS_DENIED", message: "Patient not found" } }, { status: 404 }))); renderWithProfile(<ProfileView />); expect(await screen.findByText("This health profile is not available.")).toBeVisible(); });
});
