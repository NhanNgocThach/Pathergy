import { screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import manifest from "@/app/manifest";
import { InstallPathergy } from "@/features/account/install-pathergy";
import { renderWithProviders } from "@/tests/test-utils";

describe("Pathergy progressive web app foundation", () => {
  it("provides an installable standalone manifest", () => {
    const result = manifest();

    expect(result.name).toBe("Pathergy");
    expect(result.start_url).toBe("/app");
    expect(result.scope).toBe("/");
    expect(result.display).toBe("standalone");
    expect(result.icons).toEqual(expect.arrayContaining([
      expect.objectContaining({ src: "/icon", sizes: "512x512", purpose: "any" }),
      expect.objectContaining({ src: "/icon", sizes: "512x512", purpose: "maskable" }),
    ]));
  });

  it("explains installation and the health-data caching limitation", () => {
    renderWithProviders(<InstallPathergy />);

    expect(screen.getByRole("heading", { name: "Install Pathergy on your phone" })).toBeVisible();
    expect(screen.getByRole("heading", { name: "iPhone or iPad" })).toBeVisible();
    expect(screen.getByRole("heading", { name: "Android" })).toBeVisible();
    expect(screen.getByText(/does not enable offline health-data caching/i)).toBeVisible();
  });
});
