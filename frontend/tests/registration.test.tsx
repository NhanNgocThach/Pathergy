import { describe, expect, it } from "vitest";

import { RegisterForm } from "@/features/auth/components/register-form";
import { renderWithProviders, screen, userEvent } from "@/tests/test-utils";

async function completeRegistrationForm(password = "StrongPass1!", confirmation = password) {
  const user = userEvent.setup();
  await user.type(screen.getByLabelText("Display name"), "Fictional User");
  await user.type(screen.getByLabelText("Email"), "new.user@example.com");
  await user.type(screen.getByLabelText("Password"), password);
  await user.type(screen.getByLabelText("Confirm password"), confirmation);
  await user.type(screen.getByLabelText("First name"), "Fictional");
  await user.type(screen.getByLabelText("Last name"), "User");
  await user.type(screen.getByLabelText("Date of birth"), "1990-01-01");
  await user.click(screen.getByRole("checkbox"));
  await user.click(screen.getByRole("button", { name: "Create account" }));
}

describe("RegisterForm", () => {
  it("shows weak-password validation", async () => {
    renderWithProviders(<RegisterForm />);
    await completeRegistrationForm("weak", "weak");
    expect(await screen.findByText("Password must be at least 10 characters.")).toBeVisible();
  });

  it("shows password mismatch", async () => {
    renderWithProviders(<RegisterForm />);
    await completeRegistrationForm("StrongPass1!", "Different2!");
    expect(await screen.findByText("The passwords do not match.")).toBeVisible();
  });

  it("shows verification instructions after successful registration", async () => {
    renderWithProviders(<RegisterForm />);
    await completeRegistrationForm();
    expect(await screen.findByRole("heading", { name: "Check your email" })).toBeVisible();
    expect(screen.getByText("Email verification required")).toBeVisible();
  });
});
