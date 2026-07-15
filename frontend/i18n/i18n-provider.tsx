"use client";

import * as React from "react";

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

  return <I18nContext.Provider value={{ locale, setLocale, t }}>{children}</I18nContext.Provider>;
}

export function useI18n() {
  const context = React.useContext(I18nContext);
  if (!context) throw new Error("useI18n must be used within I18nProvider");
  return context;
}
