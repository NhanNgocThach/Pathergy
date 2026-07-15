"use client";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { useI18n } from "@/i18n/i18n-provider";

export function ApplicationNotice() {
  const { t } = useI18n();
  return <Alert><AlertTitle>{t("notice.title")}</AlertTitle><AlertDescription>{t("notice.description")}</AlertDescription></Alert>;
}
