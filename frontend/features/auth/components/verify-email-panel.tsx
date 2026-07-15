"use client";

import Link from "next/link";
import * as React from "react";

import { ErrorMessage } from "@/components/error-message";
import { Spinner } from "@/components/spinner";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useI18n } from "@/i18n/i18n-provider";
import { localizeKnownText } from "@/i18n/known-text";
import { authService } from "@/services/auth-service";

export function VerifyEmailPanel({ token }: { token?: string }) {
  const { locale, t } = useI18n();
  const [state, setState] = React.useState<"loading" | "success" | "error">(token ? "loading" : "error");
  const [message, setMessage] = React.useState(token ? "" : t("auth.missingVerifyToken"));
  const attempted = React.useRef<string | null>(null);

  React.useEffect(() => {
    if (!token || attempted.current === token) return;
    attempted.current = token;
    authService.verifyEmail(token).then((result) => { setMessage(result.message); setState("success"); }).catch((error) => { setMessage(error instanceof Error ? error.message : t("auth.verifyFailed")); setState("error"); });
  }, [t, token]);

  return <Card><CardHeader><CardTitle>{t("auth.verifyTitle")}</CardTitle></CardHeader><CardContent className="space-y-4">{state === "loading" ? <Spinner label={t("auth.verifying")} /> : null}{state === "success" ? <Alert><AlertTitle>{t("auth.verified")}</AlertTitle><AlertDescription>{localizeKnownText(message, locale)}</AlertDescription></Alert> : null}{state === "error" ? <ErrorMessage title={t("auth.verifyUnavailable")} message={message} /> : null}{state !== "loading" ? <Button asChild className="w-full"><Link href="/login">{t("auth.returnLogin")}</Link></Button> : null}</CardContent></Card>;
}
