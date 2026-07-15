"use client";
import { PageHeader } from "@/components/page-header";
import { ChangePasswordForm } from "@/features/auth/components/change-password-form";
import { useI18n } from "@/i18n/i18n-provider";
export default function ChangePasswordPage() { const { t } = useI18n(); return <><PageHeader title={t("auth.changePassword")} description={t("auth.changeDescription")} /><div className="max-w-xl"><ChangePasswordForm /></div></>; }
