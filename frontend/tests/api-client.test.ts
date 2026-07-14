import { http, HttpResponse } from "msw";
import { describe, expect, it } from "vitest";

import { apiRequest } from "@/lib/api-client";
import { tokenStore } from "@/lib/token-store";
import { API_URL, tokenPair } from "@/tests/mocks/handlers";
import { server } from "@/tests/mocks/server";
import { ApiError } from "@/types/api";
import type { TokenPair } from "@/types/auth";

describe("apiRequest", () => {
  it("maps stable backend errors", async () => {
    server.use(http.get(`${API_URL}/example`, () => HttpResponse.json({ detail: { code: "INVALID_CREDENTIALS", message: "Backend wording" } }, { status: 401 })));
    await expect(apiRequest("/example", { auth: false })).rejects.toMatchObject({ code: "INVALID_CREDENTIALS", message: "The email or password is incorrect." } satisfies Partial<ApiError>);
  });

  it("clears authentication when refresh fails", async () => {
    tokenStore.setTokens(tokenPair as TokenPair);
    server.use(http.get(`${API_URL}/private`, () => new HttpResponse(null, { status: 401 })), http.post(`${API_URL}/auth/refresh`, () => HttpResponse.json({ detail: { code: "REFRESH_TOKEN_REVOKED", message: "Revoked" } }, { status: 401 })));
    await expect(apiRequest("/private")).rejects.toMatchObject({ code: "SESSION_EXPIRED" });
    expect(tokenStore.getAccessToken()).toBeNull();
    expect(tokenStore.getRefreshToken()).toBeNull();
  });

  it("uses one rotation for concurrent 401 responses and retries once", async () => {
    tokenStore.setTokens(tokenPair as TokenPair);
    let refreshCalls = 0;
    server.use(
      http.get(`${API_URL}/private`, ({ request }) => request.headers.get("Authorization") === "Bearer refreshed-access" ? HttpResponse.json({ ok: true }) : new HttpResponse(null, { status: 401 })),
      http.post(`${API_URL}/auth/refresh`, () => { refreshCalls += 1; return HttpResponse.json({ ...tokenPair, access_token: "refreshed-access", refresh_token: "rotated-refresh" }); }),
    );
    const results = await Promise.all([apiRequest<{ ok: boolean }>("/private"), apiRequest<{ ok: boolean }>("/private")]);
    expect(results).toEqual([{ ok: true }, { ok: true }]);
    expect(refreshCalls).toBe(1);
  });

  it("rejects a malformed successful response safely", async () => {
    server.use(http.get(`${API_URL}/malformed`, () => new HttpResponse("not-json", { status: 200, headers: { "Content-Type": "text/plain" } })));
    await expect(apiRequest("/malformed", { auth: false })).rejects.toMatchObject({ code: "MALFORMED_RESPONSE" });
  });

  it("does not rotate tokens for a stable credential error", async () => {
    let refreshCalls = 0;
    tokenStore.setTokens(tokenPair as TokenPair);
    server.use(http.post(`${API_URL}/protected-form`, () => HttpResponse.json({ detail: { code: "INVALID_CREDENTIALS", message: "Wrong current password" } }, { status: 401 })), http.post(`${API_URL}/auth/refresh`, () => { refreshCalls += 1; return HttpResponse.json(tokenPair); }));
    await expect(apiRequest("/protected-form", { method: "POST" })).rejects.toMatchObject({ code: "INVALID_CREDENTIALS" });
    expect(refreshCalls).toBe(0);
  });
});
