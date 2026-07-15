"use client";

import Link from "next/link";
import { useI18n } from "@/i18n/i18n-provider";
export function Pagination({ previous, next }: { previous?: string; next?: string }) { const { t } = useI18n(); return <nav aria-label={t("common.pagination")} className="flex justify-between gap-4">{previous ? <Link className="min-h-11 rounded-md border bg-card px-4 py-3 text-sm font-semibold" href={previous}>{t("common.previous")}</Link> : <span />}{next ? <Link className="min-h-11 rounded-md border bg-card px-4 py-3 text-sm font-semibold" href={next}>{t("common.next")}</Link> : null}</nav>; }
