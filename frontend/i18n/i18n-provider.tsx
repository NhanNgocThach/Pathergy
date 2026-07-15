"use client";

import * as React from "react";
import { usePathname } from "next/navigation";

import { messages, type Locale } from "@/i18n/messages";

const STORAGE_KEY = "pathergy.locale";

type I18nContextValue = {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: string, variables?: Record<string, string | number>) => string;
};

export const I18nContext = React.createContext<I18nContextValue | null>(null);

function preferredLocale(): Locale {
  const saved = window.localStorage.getItem(STORAGE_KEY);
  if (saved === "en" || saved === "vi" || saved === "zh-CN") return saved;
  const browserLocale = window.navigator.language.toLowerCase();
  if (browserLocale.startsWith("vi")) return "vi";
  if (browserLocale.startsWith("zh")) return "zh-CN";
  return "en";
}

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [locale, setLocaleState] = React.useState<Locale>("en");

  React.useEffect(() => {
    // The first server/client render stays English to avoid a hydration mismatch.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLocaleState(preferredLocale());
  }, []);
  React.useEffect(() => {
    document.documentElement.lang = locale;
    window.localStorage.setItem(STORAGE_KEY, locale);
  }, [locale]);

  const setLocale = React.useCallback((nextLocale: Locale) => setLocaleState(nextLocale), []);
  const t = React.useCallback((key: string, variables: Record<string, string | number> = {}) => {
    const template = messages[locale][key] ?? messages.en[key] ?? key;
    return Object.entries(variables).reduce(
      (value, [name, replacement]) => value.replaceAll(`{${name}}`, String(replacement)),
      template,
    );
  }, [locale]);

  React.useEffect(() => {
    const routeKey = pathname === "/login" ? "auth.login"
      : pathname === "/register" ? "register.title"
      : pathname === "/forgot-password" ? "forgot.title"
      : pathname.includes("reset-password") ? "auth.resetTitle"
      : pathname.includes("verify-email") ? "auth.verifyTitle"
      : pathname === "/app" ? "nav.dashboard"
      : pathname === "/my-health/edit" ? "profile.editTitle"
      : pathname === "/my-health" ? "profile.title"
      : pathname.includes("/allergies/") && pathname.endsWith("/edit") ? "allergy.edit"
      : pathname === "/allergies/new" ? "allergy.add"
      : pathname === "/allergies" ? "allergy.title"
      : pathname === "/medication-check/results" ? "medication.resultTitle"
      : pathname === "/medication-check" ? "medication.title"
      : pathname.startsWith("/screening-history/") ? "history.detailTitle"
      : pathname === "/screening-history" ? "history.title"
      : pathname === "/families/new" ? "family.create"
      : pathname.startsWith("/families/") ? "family.title"
      : pathname === "/families" ? "family.title"
      : pathname === "/security/sessions" ? "auth.activeSessions"
      : pathname === "/change-password" ? "auth.changePassword"
      : pathname === "/settings" ? "settings.title"
      : null;
    document.title = routeKey ? `${t(routeKey)} | Pathergy` : "Pathergy";
  }, [pathname, t]);

  return <I18nContext.Provider value={{ locale, setLocale, t }}>{children}</I18nContext.Provider>;
}

export function useI18n() {
  const context = React.useContext(I18nContext);
  if (!context) throw new Error("useI18n must be used within I18nProvider");
  return context;
}
