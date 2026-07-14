import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { AuthContext } from "@/features/auth/auth-provider";
import { AuthGuard } from "@/features/auth/auth-guard";
import { navigationMocks } from "@/tests/mocks/navigation";
import { currentUser } from "@/tests/mocks/handlers";

const functions = { login: vi.fn(), register: vi.fn(), logout: vi.fn(), refreshSession: vi.fn() };

describe("AuthGuard", () => {
  it("redirects an unauthenticated user to login", async () => {
    render(<AuthContext.Provider value={{ ...functions, user: null, isLoading: false }}><AuthGuard><p>Protected content</p></AuthGuard></AuthContext.Provider>);
    await waitFor(() => expect(navigationMocks.replace).toHaveBeenCalledWith("/login?returnTo=%2Fapp"));
    expect(screen.queryByText("Protected content")).not.toBeInTheDocument();
  });

  it("allows authenticated route access", () => {
    render(<AuthContext.Provider value={{ ...functions, user: currentUser, isLoading: false }}><AuthGuard><p>Protected content</p></AuthGuard></AuthContext.Provider>);
    expect(screen.getByText("Protected content")).toBeVisible();
  });
});
