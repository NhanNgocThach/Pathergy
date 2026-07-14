"use client";

import Link from "next/link";
import * as React from "react";

import { ErrorMessage } from "@/components/error-message";
import { Spinner } from "@/components/spinner";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { authService } from "@/services/auth-service";

export function VerifyEmailPanel({ token }: { token?: string }) {
  const [state, setState] = React.useState<"loading" | "success" | "error">(token ? "loading" : "error");
  const [message, setMessage] = React.useState(token ? "" : "The verification token is missing.");
  const attempted = React.useRef<string | null>(null);

  React.useEffect(() => {
    if (!token || attempted.current === token) return;
    attempted.current = token;
    authService.verifyEmail(token).then((result) => { setMessage(result.message); setState("success"); }).catch((error) => { setMessage(error instanceof Error ? error.message : "Email verification failed."); setState("error"); });
  }, [token]);

  return <Card><CardHeader><CardTitle>Verify email</CardTitle></CardHeader><CardContent className="space-y-4">{state === "loading" ? <Spinner label="Verifying your email" /> : null}{state === "success" ? <Alert><AlertTitle>Email verified</AlertTitle><AlertDescription>{message}</AlertDescription></Alert> : null}{state === "error" ? <ErrorMessage title="Verification link unavailable" message={message} /> : null}{state !== "loading" ? <Button asChild className="w-full"><Link href="/login">Return to login</Link></Button> : null}</CardContent></Card>;
}
