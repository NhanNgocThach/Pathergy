"use client";

import { usePathname, useRouter } from "next/navigation";
import * as React from "react";

import { Spinner } from "@/components/spinner";
import { useAuth } from "@/hooks/use-auth";
import { useI18n } from "@/i18n/i18n-provider";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth();
  const { t } = useI18n();
  const router = useRouter();
  const pathname = usePathname();

  React.useEffect(() => {
    if (!isLoading && !user) {
      router.replace(`/login?returnTo=${encodeURIComponent(pathname)}`);
    }
  }, [isLoading, pathname, router, user]);

  if (isLoading || !user) {
    return <main className="grid min-h-screen place-items-center"><Spinner label={t("common.checkingSession")} /></main>;
  }
  return children;
}
