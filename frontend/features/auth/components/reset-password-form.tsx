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
import { useI18n } from "@/i18n/i18n-provider";
import { resetPasswordSchema, type ResetPasswordValues } from "@/schemas/auth";
import { authService } from "@/services/auth-service";
export function ResetPasswordForm({ token }: { token?: string }) { const { t } = useI18n(); const [success, setSuccess] = React.useState(false); const [error, setError] = React.useState<string | null>(token ? null : t("auth.missingResetToken")); const form = useForm<ResetPasswordValues>({ resolver: zodResolver(resetPasswordSchema), defaultValues: { password: "", confirm_password: "" } }); async function onSubmit(values: ResetPasswordValues) { if (!token) return; setError(null); try { await authService.resetPassword(token, values); setSuccess(true); } catch (caught) { setError(caught instanceof Error ? caught.message : t("auth.resetFailed")); } } if (success) return <Card><CardHeader><CardTitle>{t("auth.resetDone")}</CardTitle></CardHeader><CardContent className="space-y-4"><Alert><AlertTitle>{t("auth.passwordChanged")}</AlertTitle><AlertDescription>{t("auth.resetSessions")}</AlertDescription></Alert><Button asChild className="w-full"><Link href="/login">{t("auth.returnLogin")}</Link></Button></CardContent></Card>; return <Card><CardHeader><CardTitle>{t("auth.resetTitle")}</CardTitle><CardDescription>{t("auth.resetDescription")}</CardDescription></CardHeader><CardContent><form className="space-y-5" onSubmit={form.handleSubmit(onSubmit)} noValidate>{error ? <ErrorMessage title={t("auth.resetUnavailable")} message={error} /> : null}<FormField id="password" label={t("auth.newPassword")} hint={t("register.passwordHint")} error={form.formState.errors.password?.message}><PasswordInput id="password" autoComplete="new-password" disabled={!token} aria-invalid={Boolean(form.formState.errors.password)} {...form.register("password")} /></FormField><FormField id="confirm_password" label={t("auth.confirmNewPassword")} error={form.formState.errors.confirm_password?.message}><PasswordInput id="confirm_password" autoComplete="new-password" disabled={!token} aria-invalid={Boolean(form.formState.errors.confirm_password)} {...form.register("confirm_password")} /></FormField><Button className="w-full" type="submit" disabled={!token || form.formState.isSubmitting}>{form.formState.isSubmitting ? t("auth.resetting") : t("auth.resetTitle")}</Button></form></CardContent></Card>; }
