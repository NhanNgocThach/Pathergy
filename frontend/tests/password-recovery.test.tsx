import { http, HttpResponse } from "msw";
import { describe, expect, it } from "vitest";

import { ForgotPasswordForm } from "@/features/auth/components/forgot-password-form";
import { ResetPasswordForm } from "@/features/auth/components/reset-password-form";
import { API_URL } from "@/tests/mocks/handlers";
import { server } from "@/tests/mocks/server";
import { renderWithProviders, screen, userEvent } from "@/tests/test-utils";

describe("password recovery", () => {
  it("uses a privacy-preserving forgot-password response", async () => {
    const user = userEvent.setup();
    renderWithProviders(<ForgotPasswordForm />);
    await user.type(screen.getByLabelText("Email"), "unknown@example.com");
    await user.click(screen.getByRole("button", { name: "Send reset instructions" }));
    expect(await screen.findByText("If the account exists, password reset instructions are available.")).toBeVisible();
  });

  it("shows an expired reset-token state", async () => {
    server.use(http.post(`${API_URL}/auth/reset-password`, () => HttpResponse.json({ detail: { code: "RESET_TOKEN_EXPIRED", message: "Expired" } }, { status: 400 })));
    const user = userEvent.setup();
    renderWithProviders(<ResetPasswordForm token="expired-token" />);
    await user.type(screen.getByLabelText("New password"), "StrongPass1!");
    await user.type(screen.getByLabelText("Confirm new password"), "StrongPass1!");
    await user.click(screen.getByRole("button", { name: "Reset password" }));
    expect(await screen.findByText("This password reset link has expired.")).toBeVisible();
  });
});
