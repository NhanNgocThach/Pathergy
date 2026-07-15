"use client";

import { X } from "lucide-react";
import * as React from "react";

import { Button } from "@/components/ui/button";
import { useI18n } from "@/i18n/i18n-provider";

type Toast = { id: number; title: string; description?: string };
type ToastContextValue = { notify: (title: string, description?: string) => void };

const ToastContext = React.createContext<ToastContextValue | null>(null);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const { t } = useI18n();
  const [toasts, setToasts] = React.useState<Toast[]>([]);
  const nextId = React.useRef(0);
  const dismiss = React.useCallback((id: number) => setToasts((items) => items.filter((item) => item.id !== id)), []);
  const notify = React.useCallback((title: string, description?: string) => {
    const id = ++nextId.current;
    setToasts((items) => [...items, { id, title, description }]);
    window.setTimeout(() => dismiss(id), 5000);
  }, [dismiss]);
  return <ToastContext.Provider value={{ notify }}>{children}<div className="fixed bottom-20 right-4 z-50 flex w-[min(24rem,calc(100%-2rem))] flex-col gap-2 lg:bottom-4" aria-live="polite" aria-atomic="true">{toasts.map((toast) => <div key={toast.id} className="rounded-lg border bg-card p-4 shadow-lg"><div className="flex items-start gap-3"><div className="flex-1"><p className="font-semibold">{toast.title}</p>{toast.description ? <p className="mt-1 text-sm text-muted-foreground">{toast.description}</p> : null}</div><Button variant="ghost" size="icon" aria-label={t("common.dismissNotification")} onClick={() => dismiss(toast.id)}><X className="size-4" aria-hidden="true" /></Button></div></div>)}</div></ToastContext.Provider>;
}

export function useToast() {
  const value = React.useContext(ToastContext);
  if (!value) throw new Error("useToast must be used inside ToastProvider");
  return value;
}
