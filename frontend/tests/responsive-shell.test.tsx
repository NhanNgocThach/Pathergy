import { describe, expect, it, vi } from "vitest";
import { AuthContext } from "@/features/auth/auth-provider";
import { ProtectedShell } from "@/components/protected-shell";
import { currentUser } from "@/tests/mocks/handlers";
import { renderWithProviders, screen, userEvent } from "@/tests/test-utils";
const authValue = { user: currentUser, isLoading: false, login: vi.fn(), register: vi.fn(), logout: vi.fn(), refreshSession: vi.fn() };
describe("responsive application shell", () => {
  it("exposes desktop and mobile navigation labels", async () => { const user = userEvent.setup(); renderWithProviders(<AuthContext.Provider value={authValue}><ProtectedShell><h1>Page content</h1></ProtectedShell></AuthContext.Provider>); expect(screen.getByRole("navigation", { name: "Application navigation" })).toBeInTheDocument(); expect(screen.getByRole("navigation", { name: "Mobile navigation" })).toBeInTheDocument(); await user.click(screen.getByRole("button", { name: "More" })); expect(screen.getByRole("dialog", { name: "More" })).toBeVisible(); expect(screen.getAllByRole("link", { name: "Screening History" }).length).toBeGreaterThan(0); });
});
