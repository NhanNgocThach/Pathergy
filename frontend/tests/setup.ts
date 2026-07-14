import "@testing-library/jest-dom/vitest";

import { cleanup } from "@testing-library/react";
import { afterAll, afterEach, beforeAll, vi } from "vitest";

import { tokenStore } from "@/lib/token-store";
import { server } from "@/tests/mocks/server";

process.env.NEXT_PUBLIC_API_BASE_URL = "http://api.test";

const navigationMocks = vi.hoisted(() => ({
  replace: vi.fn(),
  push: vi.fn(),
  pathname: "/app",
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace: navigationMocks.replace, push: navigationMocks.push }),
  usePathname: () => navigationMocks.pathname,
  redirect: navigationMocks.replace,
}));

globalThis.__PATHERGY_NAVIGATION_MOCKS__ = navigationMocks;

beforeAll(() => server.listen({ onUnhandledRequest: "error" }));
afterEach(() => {
  cleanup();
  server.resetHandlers();
  tokenStore.clear();
  window.sessionStorage.clear();
  navigationMocks.replace.mockReset();
  navigationMocks.push.mockReset();
});
afterAll(() => server.close());
