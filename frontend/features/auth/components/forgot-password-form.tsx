"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import * as React from "react";
import { useForm } from "react-hook-form";

import { ErrorMessage } from "@/components/error-message";
import { FormField } from "@/components/form-field";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useI18n } from "@/i18n/i18n-provider";
import { forgotPasswordSchema, type ForgotPasswordValues } from "@/schemas/auth";
import { authService } from "@/services/auth-service";
import type { DevelopmentLinkResponse } from "@/types/auth";

export function ForgotPasswordForm() {
  const { t } = useI18n();
  const [result, setResult] = React.useState<DevelopmentLinkResponse | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const form = useForm<ForgotPasswordValues>({ resolver: zodResolver(forgotPasswordSchema), defaultValues: { email: "" } });

  async function onSubmit(values: ForgotPasswordValues) {
    setError(null);
    try {
      setResult(await authService.forgotPassword(values));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "The request failed.");
    }
  }

  return <Card>
    <CardHeader><CardTitle>{t("forgot.title")}</CardTitle><CardDescription>{t("forgot.description")}</CardDescription></CardHeader>
    <CardContent>{result ? <div className="space-y-4">
      <Alert><AlertTitle>{t("forgot.check")}</AlertTitle><AlertDescription>{result.message}</AlertDescription></Alert>
      {result.development_url ? <a className="inline-flex min-h-11 items-center font-semibold text-primary underline" href={result.development_url}>{t("forgot.devLink")}</a> : null}
      <Button asChild className="w-full"><Link href="/login">{t("auth.returnLogin")}</Link></Button>
    </div> : <form className="space-y-5" onSubmit={form.handleSubmit(onSubmit)} noValidate>
      {error ? <ErrorMessage message={error} /> : null}
      <FormField id="email" label={t("auth.email")} error={form.formState.errors.email?.message}><Input id="email" type="email" autoComplete="email" aria-invalid={Boolean(form.formState.errors.email)} {...form.register("email")} /></FormField>
      <p className="text-sm text-muted-foreground">{t("forgot.privacy")}</p>
      <Button className="w-full" type="submit" disabled={form.formState.isSubmitting}>{form.formState.isSubmitting ? t("forgot.sending") : t("forgot.send")}</Button>
      <Button asChild variant="ghost" className="w-full"><Link href="/login">{t("forgot.back")}</Link></Button>
    </form>}</CardContent>
  </Card>;
}
