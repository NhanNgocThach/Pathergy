"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import * as React from "react";
import { useForm } from "react-hook-form";

import { ErrorMessage } from "@/components/error-message";
import { FormField } from "@/components/form-field";
import { PasswordInput } from "@/components/password-input";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { resetPasswordSchema, type ResetPasswordValues } from "@/schemas/auth";
import { authService } from "@/services/auth-service";

export function ResetPasswordForm({ token }: { token?: string }) {
  const [success, setSuccess] = React.useState(false);
  const [error, setError] = React.useState<string | null>(token ? null : "The password reset token is missing.");
  const form = useForm<ResetPasswordValues>({ resolver: zodResolver(resetPasswordSchema), defaultValues: { password: "", confirm_password: "" } });
  async function onSubmit(values: ResetPasswordValues) { if (!token) return; setError(null); try { await authService.resetPassword(token, values); setSuccess(true); } catch (caught) { setError(caught instanceof Error ? caught.message : "Password reset failed."); } }
  if (success) return <Card><CardHeader><CardTitle>Password reset</CardTitle></CardHeader><CardContent className="space-y-4"><Alert><AlertTitle>Password changed</AlertTitle><AlertDescription>All active sessions were revoked. Log in with your new password.</AlertDescription></Alert><Button asChild className="w-full"><Link href="/login">Return to login</Link></Button></CardContent></Card>;
  return <Card><CardHeader><CardTitle>Reset password</CardTitle><CardDescription>Create a new password. A successful reset revokes all sessions.</CardDescription></CardHeader><CardContent><form className="space-y-5" onSubmit={form.handleSubmit(onSubmit)} noValidate>{error ? <ErrorMessage title="Reset link unavailable" message={error} /> : null}<FormField id="password" label="New password" hint="At least 10 characters with uppercase, lowercase, a number, and a special character." error={form.formState.errors.password?.message}><PasswordInput id="password" autoComplete="new-password" disabled={!token} aria-invalid={Boolean(form.formState.errors.password)} {...form.register("password")} /></FormField><FormField id="confirm_password" label="Confirm new password" error={form.formState.errors.confirm_password?.message}><PasswordInput id="confirm_password" autoComplete="new-password" disabled={!token} aria-invalid={Boolean(form.formState.errors.confirm_password)} {...form.register("confirm_password")} /></FormField><Button className="w-full" type="submit" disabled={!token || form.formState.isSubmitting}>{form.formState.isSubmitting ? "Resetting…" : "Reset password"}</Button></form></CardContent></Card>;
}
