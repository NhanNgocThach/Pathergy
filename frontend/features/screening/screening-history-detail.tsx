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
import { formatDateTime } from "@/lib/format";
import { queryKeys } from "@/lib/query-keys";
import { historyService } from "@/services/health-service";
export function ScreeningHistoryDetail({ screeningId }: { screeningId: number }) { const { selectedPatientId } = useProfile(); const query = useQuery({ queryKey: queryKeys.history(selectedPatientId!), queryFn: () => historyService.list(selectedPatientId!), enabled: Boolean(selectedPatientId) }); const item = query.data?.find((record) => record.id === screeningId); return <><PageHeader title="Screening history detail" description="This page shows only fields persisted by the current backend." /><ProfileSelector />{query.isLoading ? <p role="status">Loading screening history…</p> : query.error ? <ErrorState message={query.error.message} onRetry={() => void query.refetch()} /> : !item ? <EmptyState title="Screening record not available" description="The record is not present in the selected profile's loaded history." action={<Button asChild><Link href="/screening-history">Return to history</Link></Button>} /> : <Card><CardContent className="space-y-5 pt-6"><div className="flex flex-wrap items-start justify-between gap-3"><div><p className="text-sm text-muted-foreground">Searched medication</p><h2 className="text-2xl font-bold">{item.medication_name}</h2></div><ResultBadge result={item.result} /></div><dl className="grid gap-4 sm:grid-cols-2"><div><dt className="text-sm text-muted-foreground">Normalized name</dt><dd className="font-semibold">{item.normalized_medication_name ?? "Not confirmed"}</dd></div><div><dt className="text-sm text-muted-foreground">Medication RxCUI</dt><dd className="font-semibold">{item.medication_rxcui ?? "Not confirmed"}</dd></div><div><dt className="text-sm text-muted-foreground">Checked at</dt><dd className="font-semibold">{formatDateTime(item.created_at)}</dd></div></dl><p className="rounded-md bg-muted p-4 text-sm">The history API does not store active ingredients, match details, or the original result message. Pathergy does not reconstruct missing medical details.</p><Button asChild variant="outline"><Link href="/screening-history">Back to history</Link></Button></CardContent></Card>}</>; }
