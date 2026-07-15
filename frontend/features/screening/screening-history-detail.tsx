"use client";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { EmptyState } from "@/components/empty-state";
import { ErrorState } from "@/components/feedback/error-state";
import { ResultBadge } from "@/components/health/result-badge";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { ProfileSelector } from "@/features/profiles/profile-selector";
import { useProfile } from "@/hooks/use-profile";
import { useI18n } from "@/i18n/i18n-provider";
import { formatDateTime } from "@/lib/format";
import { queryKeys } from "@/lib/query-keys";
import { historyService } from "@/services/health-service";
export function ScreeningHistoryDetail({ screeningId }: { screeningId: number }) { const { t } = useI18n(); const { selectedPatientId } = useProfile(); const query = useQuery({ queryKey: queryKeys.history(selectedPatientId!), queryFn: () => historyService.list(selectedPatientId!), enabled: Boolean(selectedPatientId) }); const item = query.data?.find((record) => record.id === screeningId); return <><PageHeader title={t("history.detailTitle")} description={t("history.detailDescription")} /><ProfileSelector />{query.isLoading ? <p role="status">{t("history.loading")}</p> : query.error ? <ErrorState message={query.error.message} onRetry={() => void query.refetch()} /> : !item ? <EmptyState title={t("history.notAvailable")} description={t("history.notAvailableDescription")} action={<Button asChild><Link href="/screening-history">{t("history.return")}</Link></Button>} /> : <Card><CardContent className="space-y-5 pt-6"><div className="flex flex-wrap items-start justify-between gap-3"><div><p className="text-sm text-muted-foreground">{t("history.searchedMedication")}</p><h2 className="text-2xl font-bold">{item.medication_name}</h2></div><ResultBadge result={item.result} /></div><dl className="grid gap-4 sm:grid-cols-2"><div><dt className="text-sm text-muted-foreground">{t("history.normalizedName")}</dt><dd className="font-semibold">{item.normalized_medication_name ?? t("common.notConfirmed")}</dd></div><div><dt className="text-sm text-muted-foreground">{t("medication.rxcui")}</dt><dd className="font-semibold">{item.medication_rxcui ?? t("common.notConfirmed")}</dd></div><div><dt className="text-sm text-muted-foreground">{t("history.checkedAt")}</dt><dd className="font-semibold">{formatDateTime(item.created_at)}</dd></div></dl><p className="rounded-md bg-muted p-4 text-sm">{t("history.limitedData")}</p><Button asChild variant="outline"><Link href="/screening-history">{t("history.back")}</Link></Button></CardContent></Card>}</>;
}
