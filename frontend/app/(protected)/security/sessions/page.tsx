"use client";
import { PageHeader } from "@/components/page-header";
import { SessionList } from "@/features/auth/components/session-list";
import { useI18n } from "@/i18n/i18n-provider";
export default function SessionsPage() { const { t } = useI18n(); return <><PageHeader title={t("auth.activeSessions")} description={t("settings.description")} /><SessionList /></>; }
