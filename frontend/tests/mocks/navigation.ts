import type { Mock } from "vitest";

declare global {
  var __PATHERGY_NAVIGATION_MOCKS__: {
    replace: Mock;
    push: Mock;
    pathname: string;
  };
}

export const navigationMocks = globalThis.__PATHERGY_NAVIGATION_MOCKS__;
