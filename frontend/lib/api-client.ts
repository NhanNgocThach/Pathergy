import { friendlyErrorMessage } from "@/lib/error-messages";
import { getApiBaseUrl } from "@/lib/env";
import { tokenStore } from "@/lib/token-store";
import { ApiError, type ValidationErrorItem } from "@/types/api";
import type { TokenPair } from "@/types/auth";

type ApiRequestOptions = Omit<RequestInit, "body"> & {
  auth?: boolean;
  json?: unknown;
};

let refreshPromise: Promise<boolean> | null = null;

async function parseApiError(response: Response): Promise<ApiError> {
  let body: unknown;
  try {
    body = await response.json();
  } catch {
    return new ApiError(
      response.status,
      "HTTP_ERROR",
      `The server returned status ${response.status}.`,
    );
  }

  const detail = (body as { detail?: unknown })?.detail;
  if (detail && typeof detail === "object" && "code" in detail) {
    const stable = detail as { code: string; message?: string };
    const fallback = stable.message ?? "The request could not be completed.";
    return new ApiError(
      response.status,
      stable.code,
      friendlyErrorMessage(stable.code, fallback),
      detail,
    );
  }
  if (typeof detail === "string") {
    return new ApiError(response.status, "HTTP_ERROR", detail, detail);
  }
  if (Array.isArray(detail)) {
    const first = detail[0] as ValidationErrorItem | undefined;
    return new ApiError(
      response.status,
      "VALIDATION_ERROR",
      first?.msg ?? "Check the form fields and try again.",
      detail,
    );
  }
  return new ApiError(
    response.status,
    "HTTP_ERROR",
    "The request could not be completed.",
    body,
  );
}

async function rawFetch(path: string, init: RequestInit): Promise<Response> {
  try {
    return await fetch(`${getApiBaseUrl()}${path}`, init);
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError(
      0,
      "NETWORK_ERROR",
      friendlyErrorMessage("NETWORK_ERROR", "Network error"),
      error,
    );
  }
}

async function parseSuccess<T>(response: Response): Promise<T> {
  try {
    return (await response.json()) as T;
  } catch (error) {
    throw new ApiError(
      response.status,
      "MALFORMED_RESPONSE",
      friendlyErrorMessage("MALFORMED_RESPONSE", "The server returned an unreadable response."),
      error,
    );
  }
}

async function rotateRefreshToken(): Promise<boolean> {
  const refreshToken = tokenStore.getRefreshToken();
  if (!refreshToken) {
    tokenStore.clear();
    return false;
  }
  const response = await rawFetch("/auth/refresh", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });
  if (!response.ok) {
    tokenStore.clear();
    return false;
  }
  const tokens = await parseSuccess<TokenPair>(response);
  if (!tokens.access_token || !tokens.refresh_token) {
    tokenStore.clear();
    return false;
  }
  tokenStore.setTokens(tokens);
  return true;
}

export async function refreshSession(): Promise<boolean> {
  if (!refreshPromise) {
    refreshPromise = rotateRefreshToken()
      .catch(() => {
        tokenStore.clear();
        return false;
      })
      .finally(() => {
        refreshPromise = null;
      });
  }
  return refreshPromise;
}

export async function apiRequest<T>(
  path: string,
  options: ApiRequestOptions = {},
  retryOnUnauthorized = true,
): Promise<T> {
  const { auth = true, json, headers: suppliedHeaders, ...init } = options;
  const headers = new Headers(suppliedHeaders);
  if (json !== undefined) headers.set("Content-Type", "application/json");
  if (auth) {
    const accessToken = tokenStore.getAccessToken();
    if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);
  }

  const response = await rawFetch(path, {
    ...init,
    headers,
    body: json === undefined ? undefined : JSON.stringify(json),
  });

  if (response.status === 401 && auth && retryOnUnauthorized) {
    const unauthorized = await parseApiError(response.clone());
    const refreshEligible = ["AUTHENTICATION_REQUIRED", "INVALID_ACCESS_TOKEN", "ACCESS_TOKEN_EXPIRED", "HTTP_ERROR"].includes(unauthorized.code);
    if (refreshEligible) {
      const refreshed = await refreshSession();
      if (refreshed) return apiRequest<T>(path, options, false);
      throw new ApiError(401, "SESSION_EXPIRED", friendlyErrorMessage("SESSION_EXPIRED", "Session expired"));
    }
    throw unauthorized;
  }
  if (!response.ok) throw await parseApiError(response);
  if (response.status === 204) return undefined as T;
  return parseSuccess<T>(response);
}
