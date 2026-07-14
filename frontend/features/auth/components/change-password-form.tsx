"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import * as React from "react";
import { useForm } from "react-hook-form";

import { ErrorMessage } from "@/components/error-message";
import { FormField } from "@/components/form-field";
import { PasswordInput } from "@/components/password-input";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { tokenStore } from "@/lib/token-store";
import { changePasswordSchema, type ChangePasswordValues } from "@/schemas/auth";
import { authService } from "@/services/auth-service";

export function ChangePasswordForm() {
  const router = useRouter();
  const [error, setError] = React.useState<string | null>(null);
  const [success, setSuccess] = React.useState(false);
  const form = useForm<ChangePasswordValues>({ resolver: zodResolver(changePasswordSchema), defaultValues: { current_password: "", password: "", confirm_password: "" } });
  async function onSubmit(values: ChangePasswordValues) { setError(null); try { await authService.changePassword(values); tokenStore.clear(); setSuccess(true); window.setTimeout(() => router.replace("/login"), 800); } catch (caught) { setError(caught instanceof Error ? caught.message : "Password change failed."); } }
  return <Card><CardHeader><CardTitle>Change password</CardTitle><CardDescription>This action signs out every device, including this one.</CardDescription></CardHeader><CardContent>{success ? <Alert><AlertTitle>Password changed</AlertTitle><AlertDescription>All sessions were revoked. Returning to login…</AlertDescription></Alert> : <form className="space-y-5" onSubmit={form.handleSubmit(onSubmit)} noValidate>{error ? <ErrorMessage message={error} /> : null}<FormField id="current_password" label="Current password" error={form.formState.errors.current_password?.message}><PasswordInput id="current_password" autoComplete="current-password" aria-invalid={Boolean(form.formState.errors.current_password)} {...form.register("current_password")} /></FormField><FormField id="password" label="New password" hint="At least 10 characters with uppercase, lowercase, a number, and a special character." error={form.formState.errors.password?.message}><PasswordInput id="password" autoComplete="new-password" aria-invalid={Boolean(form.formState.errors.password)} {...form.register("password")} /></FormField><FormField id="confirm_password" label="Confirm new password" error={form.formState.errors.confirm_password?.message}><PasswordInput id="confirm_password" autoComplete="new-password" aria-invalid={Boolean(form.formState.errors.confirm_password)} {...form.register("confirm_password")} /></FormField><Button type="submit" disabled={form.formState.isSubmitting}>{form.formState.isSubmitting ? "Changing password…" : "Change password and sign out"}</Button></form>}</CardContent></Card>;
}
