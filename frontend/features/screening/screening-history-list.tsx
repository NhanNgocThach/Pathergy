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
import { formatDateTime } from "@/lib/format";
import { queryKeys } from "@/lib/query-keys";
import { historyService } from "@/services/health-service";
import { ApiError } from "@/types/api";
import type { MedicationCheckStatus } from "@/types/health";

export function ScreeningHistoryList() { const { selected, selectedPatientId } = useProfile(); const [text, setText] = React.useState(""); const [status, setStatus] = React.useState<MedicationCheckStatus | "">(""); const query = useQuery({ queryKey: queryKeys.history(selectedPatientId!), queryFn: () => historyService.list(selectedPatientId!), enabled: Boolean(selectedPatientId), gcTime: 60_000 }); const items = (query.data ?? []).filter((item) => (!text || item.medication_name.toLocaleLowerCase().includes(text.toLocaleLowerCase()) || item.normalized_medication_name?.toLocaleLowerCase().includes(text.toLocaleLowerCase())) && (!status || item.result === status)); const denied = query.error instanceof ApiError && query.error.code === "FAMILY_PERMISSION_DENIED"; return <><PageHeader title="Screening history" description="Review the limited medication-check records currently stored by the backend." /><ProfileSelector /><div className="grid gap-4 rounded-lg border bg-card p-4 sm:grid-cols-2"><FormField id="history-search" label="Filter loaded history by medication"><Input id="history-search" value={text} onChange={(event) => setText(event.target.value)} /></FormField><FormField id="history-result" label="Filter loaded history by result"><Select id="history-result" value={status} onChange={(event) => setStatus(event.target.value as MedicationCheckStatus | "")}><option value="">All results</option><option value="POTENTIAL_ALLERGY_MATCH">Potential allergy match</option><option value="NO_RECORDED_MATCH_FOUND">No recorded match found</option><option value="UNABLE_TO_VERIFY">Unable to verify</option></Select></FormField><p className="text-xs text-muted-foreground sm:col-span-2">Filters apply only to the history loaded from the API. The backend does not currently support server filtering or pagination.</p></div>{query.isLoading ? <p role="status">Loading screening history…</p> : denied ? <PermissionDenied description="This profile has not shared screening-history view permission with you." /> : query.error ? <ErrorState message={query.error.message} onRetry={() => void query.refetch()} /> : !query.data?.length ? <EmptyState title="No medication checks have been recorded for this profile" description="Run a medication check to create the first history record." /> : !items.length ? <EmptyState title="No loaded records match these filters" description="Clear or change the client-side filters." /> : <Table aria-label={`Screening history for ${selected?.first_name ?? "selected profile"}`}><TableHeader><TableRow><TableHead>Medication</TableHead><TableHead>Normalized name</TableHead><TableHead>Result</TableHead><TableHead>Date</TableHead></TableRow></TableHeader><TableBody>{items.map((item) => <TableRow key={item.id}><TableCell><Link className="font-semibold underline-offset-4 hover:underline" href={`/screening-history/${item.id}`}>{item.medication_name}</Link></TableCell><TableCell>{item.normalized_medication_name ?? "Not confirmed"}{item.medication_rxcui ? <span className="block text-xs text-muted-foreground">RxCUI {item.medication_rxcui}</span> : null}</TableCell><TableCell><ResultBadge result={item.result} /></TableCell><TableCell>{formatDateTime(item.created_at)}</TableCell></TableRow>)}</TableBody></Table>}</>; }
