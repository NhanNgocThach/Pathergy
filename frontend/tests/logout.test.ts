import { expect, it } from "vitest";

import { tokenStore } from "@/lib/token-store";
import { authService } from "@/services/auth-service";
import { tokenPair } from "@/tests/mocks/handlers";
import type { TokenPair } from "@/types/auth";

it("clears stored authentication on logout", async () => {
  tokenStore.setTokens(tokenPair as TokenPair);
  await authService.logout();
  expect(tokenStore.getAccessToken()).toBeNull();
  expect(tokenStore.getRefreshToken()).toBeNull();
});
