"use client";

import { Button } from "@/components/ui/button";
import { StatusPanel } from "@/components/feedback/status-panel";
import { useI18n } from "@/i18n/i18n-provider";
export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) { const { t } = useI18n(); return <StatusPanel tone="error" title={t("common.requestFailed")} actions={onRetry ? <Button variant="outline" onClick={onRetry}>{t("common.tryAgain")}</Button> : undefined}><p>{message}</p></StatusPanel>; }
