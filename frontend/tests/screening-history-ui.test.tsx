import { http, HttpResponse } from "msw";
import { describe, expect, it } from "vitest";
import { ScreeningHistoryDetail } from "@/features/screening/screening-history-detail";
import { ScreeningHistoryList } from "@/features/screening/screening-history-list";
import { API_URL } from "@/tests/mocks/handlers";
import { server } from "@/tests/mocks/server";
import { renderWithProfile, screen } from "@/tests/test-utils";
describe("screening history", () => {
  it("lists stored history fields", async () => { renderWithProfile(<ScreeningHistoryList />); expect(await screen.findByRole("link", { name: "Fictional medicine" })).toBeVisible(); expect(screen.getAllByText("No recorded match found").length).toBeGreaterThan(0); });
  it("shows a detail without fabricating ingredients or matches", async () => { renderWithProfile(<ScreeningHistoryDetail screeningId={7} />); expect(await screen.findByRole("heading", { name: "Fictional medicine" })).toBeVisible(); expect(screen.getByText(/does not store active ingredients/)).toBeVisible(); });
  it("shows an empty state", async () => { server.use(http.get(`${API_URL}/patients/10/screening-history`, () => HttpResponse.json([]))); renderWithProfile(<ScreeningHistoryList />); expect(await screen.findByText("No medication checks have been recorded for this profile")).toBeVisible(); });
  it("shows permission denial", async () => { server.use(http.get(`${API_URL}/patients/10/screening-history`, () => HttpResponse.json({ detail: { code: "FAMILY_PERMISSION_DENIED", message: "Denied" } }, { status: 403 }))); renderWithProfile(<ScreeningHistoryList />); expect(await screen.findByRole("heading", { name: "Permission required" })).toBeVisible(); });
});
