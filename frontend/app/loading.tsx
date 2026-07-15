"use client";

import { Spinner } from "@/components/spinner";
import { useI18n } from "@/i18n/i18n-provider";

export default function Loading() {
  const { t } = useI18n();
  return <main className="grid min-h-screen place-items-center"><Spinner label={t("common.loadingPathergy")} /></main>;
}
