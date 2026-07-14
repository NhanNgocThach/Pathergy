import { describe, expect, it } from "vitest";

import { SessionList } from "@/features/auth/components/session-list";
import { tokenStore } from "@/lib/token-store";
import { navigationMocks } from "@/tests/mocks/navigation";
import { tokenPair } from "@/tests/mocks/handlers";
import { renderWithProviders, screen, userEvent, waitFor } from "@/tests/test-utils";
import type { TokenPair } from "@/types/auth";

describe("SessionList", () => {
  it("renders information returned by the backend", async () => {
    tokenStore.setTokens(tokenPair as TokenPair);
    renderWithProviders(<SessionList />);
    expect(await screen.findByText("Fictional browser")).toBeVisible();
    expect(screen.getByText("Current session")).toBeVisible();
    expect(screen.getByText("Pathergy Test Browser")).toBeVisible();
  });

  it("revokes the current session and returns to login", async () => {
    tokenStore.setTokens(tokenPair as TokenPair);
    const user = userEvent.setup();
    renderWithProviders(<SessionList />);
    await user.click(await screen.findByRole("button", { name: "Revoke" }));
    await user.click(screen.getByRole("button", { name: "Revoke session" }));
    await waitFor(() => expect(navigationMocks.replace).toHaveBeenCalledWith("/login"));
    expect(tokenStore.getAccessToken()).toBeNull();
  });
});
