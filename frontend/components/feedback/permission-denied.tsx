"use client";

import { LockKeyhole } from "lucide-react";
import { EmptyState } from "@/components/empty-state";
import { useI18n } from "@/i18n/i18n-provider";
export function PermissionDenied({ description }: { description?: string }) { const { t } = useI18n(); return <EmptyState icon={LockKeyhole} title={t("common.permissionRequired")} description={description ?? t("common.permissionDefault")} />; }
