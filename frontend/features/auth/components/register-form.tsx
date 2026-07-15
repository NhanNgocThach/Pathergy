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
import { Input } from "@/components/ui/input";
import { useAuth } from "@/hooks/use-auth";
import { useI18n } from "@/i18n/i18n-provider";
import { registerSchema, type RegisterValues } from "@/schemas/auth";
import type { RegisterResponse } from "@/types/auth";

const defaults: RegisterValues = { display_name: "", email: "", password: "", confirm_password: "", first_name: "", last_name: "", date_of_birth: "", accept_notices: false };

export function RegisterForm() {
  const { register } = useAuth();
  const { t } = useI18n();
  const [serverError, setServerError] = React.useState<string | null>(null);
  const [result, setResult] = React.useState<RegisterResponse | null>(null);
  const form = useForm<RegisterValues>({ resolver: zodResolver(registerSchema), defaultValues: defaults });

  async function onSubmit(values: RegisterValues) {
    setServerError(null);
    try { setResult(await register(values)); } catch (error) { setServerError(error instanceof Error ? error.message : "Registration failed."); }
  }

  if (result) {
    return <Card><CardHeader><CardTitle>{t("register.checkEmail")}</CardTitle><CardDescription>{t("register.created")}</CardDescription></CardHeader><CardContent className="space-y-4"><Alert><AlertTitle>{t("register.verificationRequired")}</AlertTitle><AlertDescription>{t("register.verificationHelp")}</AlertDescription></Alert>{result.verification_url ? <a className="inline-flex min-h-11 items-center font-semibold text-primary underline" href={result.verification_url}>{t("register.devLink")}</a> : null}<Button asChild className="w-full"><Link href="/login">{t("auth.returnLogin")}</Link></Button></CardContent></Card>;
  }

  return (
    <Card>
      <CardHeader><CardTitle>{t("register.title")}</CardTitle><CardDescription>{t("register.description")}</CardDescription></CardHeader>
      <CardContent><form className="space-y-5" onSubmit={form.handleSubmit(onSubmit)} noValidate>
        {serverError ? <ErrorMessage message={serverError} title={t("register.failed")} /> : null}
        <fieldset className="space-y-4"><legend className="text-lg font-bold">{t("register.account")}</legend>
          <FormField id="display_name" label={t("register.displayName")} error={form.formState.errors.display_name?.message}><Input id="display_name" autoComplete="name" aria-invalid={Boolean(form.formState.errors.display_name)} {...form.register("display_name")} /></FormField>
          <FormField id="email" label={t("auth.email")} error={form.formState.errors.email?.message}><Input id="email" type="email" autoComplete="email" aria-invalid={Boolean(form.formState.errors.email)} {...form.register("email")} /></FormField>
          <FormField id="password" label={t("auth.password")} hint={t("register.passwordHint")} error={form.formState.errors.password?.message}><PasswordInput id="password" autoComplete="new-password" aria-invalid={Boolean(form.formState.errors.password)} {...form.register("password")} /></FormField>
          <FormField id="confirm_password" label={t("register.confirmPassword")} error={form.formState.errors.confirm_password?.message}><PasswordInput id="confirm_password" autoComplete="new-password" aria-invalid={Boolean(form.formState.errors.confirm_password)} {...form.register("confirm_password")} /></FormField>
        </fieldset>
        <fieldset className="space-y-4"><legend className="text-lg font-bold">{t("register.profile")}</legend>
          <FormField id="first_name" label={t("register.firstName")} error={form.formState.errors.first_name?.message}><Input id="first_name" autoComplete="given-name" aria-invalid={Boolean(form.formState.errors.first_name)} {...form.register("first_name")} /></FormField>
          <FormField id="last_name" label={t("register.lastName")} error={form.formState.errors.last_name?.message}><Input id="last_name" autoComplete="family-name" aria-invalid={Boolean(form.formState.errors.last_name)} {...form.register("last_name")} /></FormField>
          <FormField id="date_of_birth" label={t("register.birthDate")} error={form.formState.errors.date_of_birth?.message}><Input id="date_of_birth" type="date" autoComplete="bday" aria-invalid={Boolean(form.formState.errors.date_of_birth)} {...form.register("date_of_birth")} /></FormField>
        </fieldset>
        <div><label className="flex items-start gap-3 text-sm"><input className="mt-1 size-5" type="checkbox" aria-describedby="notices-help notices-error" {...form.register("accept_notices")} /><span>{t("register.consent")}</span></label><p id="notices-help" className="mt-2 text-sm text-muted-foreground">{t("register.familyNotice")}</p>{form.formState.errors.accept_notices ? <p id="notices-error" className="mt-2 text-sm font-medium text-destructive">{form.formState.errors.accept_notices.message}</p> : null}</div>
        <Button className="w-full" type="submit" disabled={form.formState.isSubmitting}>{form.formState.isSubmitting ? t("register.creating") : t("register.title")}</Button>
        <p className="text-center text-sm">{t("register.already")} <Link className="font-semibold text-primary underline-offset-4 hover:underline" href="/login">{t("auth.login")}</Link></p>
      </form></CardContent>
    </Card>
  );
}
