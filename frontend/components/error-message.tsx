"use client";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { useI18n } from "@/i18n/i18n-provider";
import { localizeKnownText } from "@/i18n/known-text";

export function ErrorMessage({ message, title }: { message: string; title?: string }) {
  const { locale, t } = useI18n();
  return <Alert variant="destructive"><AlertTitle>{title ?? t("error.defaultTitle")}</AlertTitle><AlertDescription>{localizeKnownText(message, locale)}</AlertDescription></Alert>;
}
