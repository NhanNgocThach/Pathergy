import { http, HttpResponse } from "msw";
import { describe, expect, it } from "vitest";

import { LoginForm } from "@/features/auth/components/login-form";
import { navigationMocks } from "@/tests/mocks/navigation";
import { API_URL } from "@/tests/mocks/handlers";
import { server } from "@/tests/mocks/server";
import { renderWithProviders, screen, userEvent, waitFor } from "@/tests/test-utils";

describe("LoginForm", () => {
  it("validates required fields and exposes accessible labels", async () => {
    const user = userEvent.setup();
    renderWithProviders(<LoginForm />);
    expect(screen.getByLabelText("Email")).toHaveAttribute("type", "email");
    expect(screen.getByLabelText("Password")).toHaveAttribute("type", "password");
    await user.click(screen.getByRole("button", { name: "Log in" }));
    expect(await screen.findByText("Enter a valid email address.")).toBeVisible();
    expect(screen.getByText("Enter your password.")).toBeVisible();
  });

  it("supports keyboard navigation and password visibility", async () => {
    const user = userEvent.setup();
    renderWithProviders(<LoginForm />);
    await user.tab();
    expect(screen.getByLabelText("Email")).toHaveFocus();
    await user.tab();
    expect(screen.getByLabelText("Password")).toHaveFocus();
    await user.tab();
    expect(screen.getByRole("button", { name: "Show password" })).toHaveFocus();
  });

  it("logs in successfully with the mocked API", async () => {
    let loginBody: Record<string, unknown> | undefined;
    server.use(
      http.post(`${API_URL}/auth/login`, async ({ request }) => {
        loginBody = (await request.json()) as Record<string, unknown>;
        return HttpResponse.json({
          access_token: "access-token",
          refresh_token: "refresh-token",
          token_type: "bearer",
          access_token_expires_in: 900,
          refresh_token_expires_in: 2_592_000,
        });
      }),
    );
    const user = userEvent.setup();
    renderWithProviders(<LoginForm />);
    await user.type(screen.getByLabelText("Email"), "fictional.user@example.com");
    await user.type(screen.getByLabelText("Password"), "StrongPass1!");
    await user.click(screen.getByRole("button", { name: "Log in" }));
    await waitFor(() => expect(navigationMocks.replace).toHaveBeenCalledWith("/app"));
    expect(loginBody).toMatchObject({
      device_name: "Web browser",
      device_type: "browser",
    });
  });

  it.each([
    ["INVALID_CREDENTIALS", "The email or password is incorrect."],
    ["EMAIL_NOT_VERIFIED", "Verify your email before logging in."],
  ])("shows the %s backend state", async (code, expectedMessage) => {
    server.use(http.post(`${API_URL}/auth/login`, () => HttpResponse.json({ detail: { code, message: "Backend message" } }, { status: code === "EMAIL_NOT_VERIFIED" ? 403 : 401 })));
    const user = userEvent.setup();
    renderWithProviders(<LoginForm />);
    await user.type(screen.getByLabelText("Email"), "fictional.user@example.com");
    await user.type(screen.getByLabelText("Password"), "StrongPass1!");
    await user.click(screen.getByRole("button", { name: "Log in" }));
    expect(await screen.findByText(expectedMessage)).toBeVisible();
  });
});
