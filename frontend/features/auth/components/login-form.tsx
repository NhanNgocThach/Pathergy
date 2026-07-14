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
import { loginSchema, type LoginValues } from "@/schemas/auth";

export function LoginForm({ returnTo = "/app" }: { returnTo?: string }) {
  const { login } = useAuth();
  const router = useRouter();
  const [serverError, setServerError] = React.useState<string | null>(null);
  const form = useForm<LoginValues>({ resolver: zodResolver(loginSchema), defaultValues: { email: "", password: "" } });

  async function onSubmit(values: LoginValues) {
    setServerError(null);
    try {
      await login(values);
      router.replace(returnTo.startsWith("/") ? returnTo : "/app");
    } catch (error) {
      setServerError(error instanceof Error ? error.message : "Login failed.");
    }
  }

  return (
    <Card>
      <CardHeader><CardTitle>Log in</CardTitle><CardDescription>Use your verified Pathergy account.</CardDescription></CardHeader>
      <CardContent>
        <form className="space-y-5" onSubmit={form.handleSubmit(onSubmit)} noValidate>
          {serverError ? <ErrorMessage message={serverError} title="Login unsuccessful" /> : null}
          <FormField id="email" label="Email" error={form.formState.errors.email?.message}>
            <Input id="email" type="email" autoComplete="email" aria-invalid={Boolean(form.formState.errors.email)} aria-describedby={form.formState.errors.email ? "email-error" : undefined} {...form.register("email")} />
          </FormField>
          <FormField id="password" label="Password" error={form.formState.errors.password?.message}>
            <PasswordInput id="password" autoComplete="current-password" aria-invalid={Boolean(form.formState.errors.password)} aria-describedby={form.formState.errors.password ? "password-error" : undefined} {...form.register("password")} />
          </FormField>
          <p className="text-sm text-muted-foreground">This foundation keeps sign-in for this browser tab. A remember-device option is not currently supported.</p>
          <Button className="w-full" type="submit" disabled={form.formState.isSubmitting}>{form.formState.isSubmitting ? "Logging in…" : "Log in"}</Button>
          <div className="flex flex-wrap justify-between gap-3 text-sm"><Link className="font-semibold text-primary underline-offset-4 hover:underline" href="/forgot-password">Forgot password?</Link><Link className="font-semibold text-primary underline-offset-4 hover:underline" href="/register">Create account</Link></div>
        </form>
      </CardContent>
    </Card>
  );
}
