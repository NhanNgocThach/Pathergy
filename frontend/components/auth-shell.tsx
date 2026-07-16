"use client";

import type { ReactNode } from "react";

import { ApplicationNotice } from "@/components/application-notice";
import { LanguageSelector } from "@/components/language-selector";
import { useI18n } from "@/i18n/i18n-provider";

export function AuthShell({ children }: { children: ReactNode }) {
  const { t } = useI18n();
  return <main id="main-content" className="mx-auto flex min-h-[100dvh] w-full max-w-lg flex-col justify-center gap-6 px-4 pb-[calc(2.5rem+env(safe-area-inset-bottom))] pt-[calc(2.5rem+env(safe-area-inset-top))]"><div className="flex justify-end"><LanguageSelector /></div><header className="text-center"><p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">Pathergy</p><h1 className="mt-2 text-3xl font-bold">{t("brand.tagline")}</h1></header>{children}<ApplicationNotice /></main>;
}
