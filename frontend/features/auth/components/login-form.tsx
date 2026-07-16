"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import Link from "next/link";
import { useRouter } from "next/navigation";
import * as React from "react";
import { useForm } from "react-hook-form";

import { ErrorMessage } from "@/components/error-message";
import { FormField } from "@/components/form-field";
import { PasswordInput } from "@/components/password-input";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/hooks/use-auth";
import { useI18n } from "@/i18n/i18n-provider";
import { loginSchema, type LoginValues } from "@/schemas/auth";

export function LoginForm({ returnTo = "/app" }: { returnTo?: string }) {
  const { login } = useAuth();
  const { t } = useI18n();
  const router = useRouter();
  const [serverError, setServerError] = React.useState<string | null>(null);
  const form = useForm<LoginValues>({ resolver: zodResolver(loginSchema), defaultValues: { identifier: "", password: "" } });

  async function onSubmit(values: LoginValues) {
    setServerError(null);
    try {
      await login(values);
      router.replace(returnTo.startsWith("/") ? returnTo : "/app");
    } catch (error) {
      setServerError(error instanceof Error ? error.message : t("auth.loginFallback"));
    }
  }

  return (
    <Card>
      <CardHeader><CardTitle>{t("auth.login")}</CardTitle><CardDescription>{t("auth.loginDescription")}</CardDescription></CardHeader>
      <CardContent>
        <form className="space-y-5" onSubmit={form.handleSubmit(onSubmit)} noValidate>
          {serverError ? <ErrorMessage message={serverError} title={t("auth.loginFailed")} /> : null}
          <FormField id="identifier" label={t("auth.emailOrPhone")} hint={t("auth.phoneLoginHint")} error={form.formState.errors.identifier?.message}>
            <Input id="identifier" type="text" autoComplete="username" autoCapitalize="none" spellCheck={false} aria-invalid={Boolean(form.formState.errors.identifier)} aria-describedby={form.formState.errors.identifier ? "identifier-error" : undefined} {...form.register("identifier")} />
          </FormField>
          <FormField id="password" label={t("auth.password")} error={form.formState.errors.password?.message}>
            <PasswordInput id="password" autoComplete="current-password" aria-invalid={Boolean(form.formState.errors.password)} aria-describedby={form.formState.errors.password ? "password-error" : undefined} {...form.register("password")} />
          </FormField>
          <p className="text-sm text-muted-foreground">{t("auth.sessionNotice")}</p>
          <Button className="w-full" type="submit" disabled={form.formState.isSubmitting}>{form.formState.isSubmitting ? t("auth.loggingIn") : t("auth.login")}</Button>
          <div className="flex flex-wrap justify-between gap-3 text-sm"><Link className="font-semibold text-primary underline-offset-4 hover:underline" href="/forgot-password">{t("auth.forgot")}</Link><Link className="font-semibold text-primary underline-offset-4 hover:underline" href="/register">{t("auth.create")}</Link></div>
        </form>
      </CardContent>
    </Card>
  );
}
