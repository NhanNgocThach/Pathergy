import { http, HttpResponse } from "msw";
import { describe, expect, it, vi } from "vitest";
import { AuthContext } from "@/features/auth/auth-provider";
import { FamilyCreate } from "@/features/families/family-create";
import { FamilyDetail } from "@/features/families/family-detail";
import { FamilyList } from "@/features/families/family-list";
import { PermissionEditor } from "@/features/permissions/permission-editor";
import { API_URL, currentUser, familyEntries } from "@/tests/mocks/handlers";
import { server } from "@/tests/mocks/server";
import { renderWithProviders, screen, userEvent } from "@/tests/test-utils";

const authValue = { user: currentUser, isLoading: false, login: vi.fn(), register: vi.fn(), logout: vi.fn(), refreshSession: vi.fn() };
function renderAuthenticated(ui: React.ReactElement) { return renderWithProviders(<AuthContext.Provider value={authValue}>{ui}</AuthContext.Provider>); }

describe("families", () => {
  it("lists multiple memberships independently, including inactive history", async () => { server.use(http.get(`${API_URL}/users/1/family-groups`, () => HttpResponse.json([...familyEntries, { family_group: { ...familyEntries[0].family_group, family_group_id: 6, name: "Historical Household" }, membership: { ...familyEntries[0].membership, membership_id: 60, family_group_id: 6, status: "LEFT", left_at: "2026-02-01T00:00:00Z" } }]))); renderAuthenticated(<FamilyList />); expect(await screen.findByText("Fictional Household")).toBeVisible(); expect(screen.getByText("Historical Household")).toBeVisible(); expect(screen.getByText("Historical or pending memberships do not have normal family-group access.")).toBeVisible(); });
  it("creates a family group", async () => { const user = userEvent.setup(); renderAuthenticated(<FamilyCreate />); await user.type(screen.getByLabelText("Family group name"), "Another Fictional Household"); await user.click(screen.getByRole("button", { name: "Create family group" })); expect(screen.queryByText("Unable to continue")).not.toBeInTheDocument(); });
  it("shows owner management controls and member IDs", async () => { renderAuthenticated(<FamilyDetail familyId={5} />); expect(await screen.findByText("User #2")).toBeVisible(); expect(screen.getByRole("heading", { name: "Add existing user" })).toBeVisible(); expect(screen.getByText(/roles and health-data sharing permissions are separate/i)).toBeVisible(); });
  it("submits stable family codes while showing translated option labels", async () => {
    let submitted: Record<string, unknown> | null = null;
    server.use(http.post(`${API_URL}/family-groups/5/members`, async ({ request }) => {
      submitted = await request.json() as Record<string, unknown>;
      return HttpResponse.json({ membership_id: 52, family_group_id: 5, status: "PENDING", joined_at: null, left_at: null, created_at: "2026-01-02T00:00:00Z", updated_at: "2026-01-02T00:00:00Z", ...submitted }, { status: 201 });
    }));
    const user = userEvent.setup();
    renderAuthenticated(<FamilyDetail familyId={5} />);
    await user.clear(await screen.findByLabelText("Existing Pathergy user ID"));
    await user.type(screen.getByLabelText("Existing Pathergy user ID"), "3");
    await user.selectOptions(screen.getByLabelText("Initial role"), "ADMIN");
    await user.selectOptions(screen.getAllByLabelText("Relationship")[0], "CAREGIVER");
    await user.click(screen.getByRole("button", { name: "Add pending member" }));
    await vi.waitFor(() => expect(submitted).toEqual({ user_id: 3, role: "ADMIN", relationship: "CAREGIVER" }));
  });
  it("edits only the current user's enforced permission types", async () => { const user = userEvent.setup(); renderAuthenticated(<PermissionEditor groupId={5} userId={1} />); expect((await screen.findAllByText("Basic profile")).length).toBeGreaterThan(0); expect(screen.queryByText("Medical documents")).not.toBeInTheDocument(); await user.click(screen.getAllByLabelText("Can view")[0]); await user.click(screen.getByRole("button", { name: "Save sharing permissions" })); expect(await screen.findByText("Sharing permissions saved")).toBeVisible(); });
  it("shows the final-owner restriction from the backend", async () => { server.use(http.post(`${API_URL}/family-groups/5/members/1/leave`, () => HttpResponse.json({ detail: { code: "LAST_OWNER_CANNOT_LEAVE", message: "Transfer ownership" } }, { status: 409 }))); const user = userEvent.setup(); renderAuthenticated(<FamilyDetail familyId={5} />); await user.click(await screen.findByRole("button", { name: "Leave family group" })); await user.click(screen.getByRole("button", { name: "Leave family" })); expect(await screen.findByText("Add or transfer another active owner before changing the final owner.")).toBeVisible(); });
});
