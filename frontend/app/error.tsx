"use client";

import { ErrorMessage } from "@/components/error-message";
import { Button } from "@/components/ui/button";
import { useI18n } from "@/i18n/i18n-provider";

export default function GlobalError({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  const { t } = useI18n();
  return <main className="mx-auto flex min-h-screen max-w-xl flex-col justify-center gap-4 px-4"><ErrorMessage title={t("common.unexpectedError")} message={t("common.unexpectedErrorDescription")} /><Button onClick={reset}>{t("common.tryAgain")}</Button></main>;
}
