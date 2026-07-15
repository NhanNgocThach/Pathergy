import { screen, waitFor } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { AuthShell } from "@/components/auth-shell";
import { renderWithProviders, userEvent } from "@/tests/test-utils";

describe("language selection", () => {
  it("switches the shared interface to Vietnamese and persists the choice", async () => {
    const user = userEvent.setup();
    renderWithProviders(<AuthShell><div>content</div></AuthShell>);

    await user.selectOptions(screen.getByRole("combobox", { name: "Language" }), "vi");

    expect(screen.getByRole("heading", { name: "Quản lý sức khỏe cá nhân rõ ràng" })).toBeInTheDocument();
    await waitFor(() => expect(document.documentElement.lang).toBe("vi"));
    expect(window.localStorage.getItem("pathergy.locale")).toBe("vi");
  });

  it("switches the shared interface to Simplified Chinese", async () => {
    const user = userEvent.setup();
    renderWithProviders(<AuthShell><div>content</div></AuthShell>);

    await user.selectOptions(screen.getByRole("combobox", { name: "Language" }), "zh-CN");

    expect(screen.getByRole("heading", { name: "清晰管理个人健康" })).toBeInTheDocument();
  });
});
