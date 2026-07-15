"use client";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import * as React from "react";
import { EmptyState } from "@/components/empty-state";
import { ErrorState } from "@/components/feedback/error-state";
import { PermissionDenied } from "@/components/feedback/permission-denied";
import { ResultBadge } from "@/components/health/result-badge";
import { FormField } from "@/components/form-field";
import { PageHeader } from "@/components/page-header";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ProfileSelector } from "@/features/profiles/profile-selector";
import { useProfile } from "@/hooks/use-profile";
import { useI18n } from "@/i18n/i18n-provider";
import { formatDateTime } from "@/lib/format";
import { queryKeys } from "@/lib/query-keys";
import { historyService } from "@/services/health-service";
import { ApiError } from "@/types/api";
import type { MedicationCheckStatus } from "@/types/health";

export function ScreeningHistoryList() {
  const { t } = useI18n(); const { selected, selectedPatientId } = useProfile(); const [text, setText] = React.useState(""); const [status, setStatus] = React.useState<MedicationCheckStatus | "">(""); const query = useQuery({ queryKey: queryKeys.history(selectedPatientId!), queryFn: () => historyService.list(selectedPatientId!), enabled: Boolean(selectedPatientId), gcTime: 60_000 }); const items = (query.data ?? []).filter((item) => (!text || item.medication_name.toLocaleLowerCase().includes(text.toLocaleLowerCase()) || item.normalized_medication_name?.toLocaleLowerCase().includes(text.toLocaleLowerCase())) && (!status || item.result === status)); const denied = query.error instanceof ApiError && query.error.code === "FAMILY_PERMISSION_DENIED";
  return <><PageHeader title={t("history.title")} description={t("history.description")} /><ProfileSelector /><div className="grid gap-4 rounded-lg border bg-card p-4 sm:grid-cols-2"><FormField id="history-search" label={t("history.filterMedication")}><Input id="history-search" value={text} onChange={(event) => setText(event.target.value)} /></FormField><FormField id="history-result" label={t("history.filterResult")}><Select id="history-result" value={status} onChange={(event) => setStatus(event.target.value as MedicationCheckStatus | "")}><option value="">{t("history.allResults")}</option><option value="POTENTIAL_ALLERGY_MATCH">{t("result.POTENTIAL_ALLERGY_MATCH")}</option><option value="NO_RECORDED_MATCH_FOUND">{t("result.NO_RECORDED_MATCH_FOUND")}</option><option value="UNABLE_TO_VERIFY">{t("result.UNABLE_TO_VERIFY")}</option></Select></FormField><p className="text-xs text-muted-foreground sm:col-span-2">{t("history.filterHint")}</p></div>{query.isLoading ? <p role="status">{t("history.loading")}</p> : denied ? <PermissionDenied description={t("history.permission")} /> : query.error ? <ErrorState message={query.error.message} onRetry={() => void query.refetch()} /> : !query.data?.length ? <EmptyState title={t("history.empty")} description={t("history.emptyDescription")} /> : !items.length ? <EmptyState title={t("history.noFilterMatches")} description={t("history.noFilterMatchesDescription")} /> : <Table aria-label={t("history.tableLabel", { name: selected?.first_name ?? t("allergy.selectedProfile") })}><TableHeader><TableRow><TableHead>{t("history.medication")}</TableHead><TableHead>{t("history.normalizedName")}</TableHead><TableHead>{t("history.result")}</TableHead><TableHead>{t("history.date")}</TableHead></TableRow></TableHeader><TableBody>{items.map((item) => <TableRow key={item.id}><TableCell><Link className="font-semibold underline-offset-4 hover:underline" href={`/screening-history/${item.id}`}>{item.medication_name}</Link></TableCell><TableCell>{item.normalized_medication_name ?? t("common.notConfirmed")}{item.medication_rxcui ? <span className="block text-xs text-muted-foreground">RxCUI {item.medication_rxcui}</span> : null}</TableCell><TableCell><ResultBadge result={item.result} /></TableCell><TableCell>{formatDateTime(item.created_at)}</TableCell></TableRow>)}</TableBody></Table>}</>;
}
