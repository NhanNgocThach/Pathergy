"use client";

import { ErrorMessage } from "@/components/error-message";
import { Button } from "@/components/ui/button";

export default function GlobalError({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return <main className="mx-auto flex min-h-screen max-w-xl flex-col justify-center gap-4 px-4"><ErrorMessage title="Pathergy encountered an unexpected error" message="Try the request again. No medical conclusion should be drawn from an application error." /><Button onClick={reset}>Try again</Button></main>;
}
