"use client";

import Link from "next/link";

import { Button } from "@/components/ui/button";
import { useI18n } from "@/i18n/i18n-provider";

export default function NotFound() {
  const { t } = useI18n();
  return <main className="mx-auto flex min-h-screen max-w-lg flex-col items-center justify-center gap-4 px-4 text-center"><p className="text-sm font-semibold text-primary">404</p><h1 className="text-3xl font-bold">{t("common.pageNotFound")}</h1><p className="text-muted-foreground">{t("common.pageNotFoundDescription")}</p><Button asChild><Link href="/">{t("common.returnPathergy")}</Link></Button></main>;
}
