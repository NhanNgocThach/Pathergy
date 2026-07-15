"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import * as React from "react";

import { AuthProvider } from "@/features/auth/auth-provider";
import { ToastProvider } from "@/components/feedback/toast-provider";
import { I18nProvider } from "@/i18n/i18n-provider";

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = React.useState(() => new QueryClient({ defaultOptions: { queries: { retry: 1, staleTime: 30_000, gcTime: 60_000, refetchOnWindowFocus: false }, mutations: { retry: false } } }));
  return <I18nProvider><QueryClientProvider client={queryClient}><AuthProvider><ToastProvider>{children}</ToastProvider></AuthProvider></QueryClientProvider></I18nProvider>;
}
