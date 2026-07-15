"use client";

import { Languages } from "lucide-react";

import { useI18n } from "@/i18n/i18n-provider";
import { localeLabels, type Locale } from "@/i18n/messages";

export function LanguageSelector({ compact = false }: { compact?: boolean }) {
  const { locale, setLocale, t } = useI18n();
  return <label className="inline-flex min-h-11 items-center gap-2 text-sm font-semibold text-muted-foreground">
    <Languages className="size-4" aria-hidden="true" />
    <span className={compact ? "sr-only" : undefined}>{t("language.label")}</span>
    <select
      className="min-h-10 rounded-md border bg-background px-2 text-foreground"
      aria-label={t("language.label")}
      value={locale}
      onChange={(event) => setLocale(event.target.value as Locale)}
    >
      {Object.entries(localeLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
    </select>
  </label>;
}
