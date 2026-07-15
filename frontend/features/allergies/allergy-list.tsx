"use client";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Pencil, Plus, Trash2 } from "lucide-react";
import Link from "next/link";
import { EmptyState } from "@/components/empty-state";
import { ErrorState } from "@/components/feedback/error-state";
import { PermissionDenied } from "@/components/feedback/permission-denied";
import { SeverityBadge } from "@/components/health/severity-badge";
import { PageHeader } from "@/components/page-header";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { ProfileSelector } from "@/features/profiles/profile-selector";
import { useProfile } from "@/hooks/use-profile";
import { useI18n } from "@/i18n/i18n-provider";
import { queryKeys } from "@/lib/query-keys";
import { allergyService } from "@/services/health-service";
import { ApiError } from "@/types/api";
import type { Allergy } from "@/types/health";

function DeleteAllergy({ allergy }: { allergy: Allergy }) {
  const { t } = useI18n(); const client = useQueryClient(); const mutation = useMutation({ mutationFn: () => allergyService.remove(allergy.patient_id, allergy.id), onSuccess: () => void client.invalidateQueries({ queryKey: queryKeys.allergies(allergy.patient_id) }) });
  return <AlertDialog><AlertDialogTrigger asChild><Button variant="ghost" size="icon" aria-label={t("allergy.deleteLabel", { substance: allergy.substance })}><Trash2 className="size-4" /></Button></AlertDialogTrigger><AlertDialogContent><AlertDialogHeader><AlertDialogTitle>{t("allergy.deleteTitle")}</AlertDialogTitle><AlertDialogDescription>{t("allergy.deleteDescription", { substance: allergy.substance })}</AlertDialogDescription></AlertDialogHeader>{mutation.error ? <p role="alert" className="text-sm text-destructive">{mutation.error.message}</p> : null}<AlertDialogFooter><AlertDialogCancel>{t("common.cancel")}</AlertDialogCancel><AlertDialogAction onClick={(event) => { event.preventDefault(); mutation.mutate(); }}>{t("allergy.deleteRecord")}</AlertDialogAction></AlertDialogFooter></AlertDialogContent></AlertDialog>;
}

export function AllergyList() {
  const { t } = useI18n(); const { selected, selectedPatientId } = useProfile(); const query = useQuery({ queryKey: queryKeys.allergies(selectedPatientId!), queryFn: () => allergyService.list(selectedPatientId!), enabled: Boolean(selectedPatientId), gcTime: 60_000 }); const denied = query.error instanceof ApiError && query.error.code === "FAMILY_PERMISSION_DENIED";
  return <><PageHeader title={t("allergy.title")} description={selected?.isOwn ? t("allergy.descriptionOwn") : t("allergy.descriptionShared")} actions={<Button asChild><Link href="/allergies/new"><Plus className="size-4" />{t("allergy.add")}</Link></Button>} /><ProfileSelector />{query.isLoading ? <p role="status">{t("allergy.loading")}</p> : denied ? <PermissionDenied description={t("allergy.permission")} /> : query.error ? <ErrorState message={query.error.message} onRetry={() => void query.refetch()} /> : !query.data?.length ? <EmptyState title={t("allergy.empty")} description={t("allergy.emptyDescription")} action={<Button asChild><Link href="/allergies/new">{t("allergy.add")}</Link></Button>} /> : <><div className="hidden md:block"><Table aria-label={t("allergy.tableLabel", { name: selected?.first_name ?? t("allergy.selectedProfile") })}><TableHeader><TableRow><TableHead>{t("allergy.substance")}</TableHead><TableHead>{t("allergy.reaction")}</TableHead><TableHead>{t("allergy.severity")}</TableHead><TableHead>RxCUI</TableHead><TableHead><span className="sr-only">{t("common.actions")}</span></TableHead></TableRow></TableHeader><TableBody>{query.data.map((allergy) => <TableRow key={allergy.id}><TableCell className="font-semibold">{allergy.substance}</TableCell><TableCell>{allergy.reaction ?? t("common.notRecorded")}</TableCell><TableCell><SeverityBadge severity={allergy.severity} /></TableCell><TableCell>{allergy.rxcui ?? "—"}</TableCell><TableCell><div className="flex justify-end"><Button asChild variant="ghost" size="icon"><Link aria-label={t("allergy.editLabel", { substance: allergy.substance })} href={`/allergies/${allergy.id}/edit`}><Pencil className="size-4" /></Link></Button><DeleteAllergy allergy={allergy} /></div></TableCell></TableRow>)}</TableBody></Table></div><div className="grid gap-4 md:hidden">{query.data.map((allergy) => <Card key={allergy.id}><CardContent className="space-y-3 pt-6"><div className="flex items-start justify-between gap-3"><h2 className="font-bold">{allergy.substance}</h2><SeverityBadge severity={allergy.severity} /></div><p><span className="text-sm text-muted-foreground">{t("allergy.reaction")}:</span> {allergy.reaction ?? t("common.notRecorded")}</p><p><span className="text-sm text-muted-foreground">RxCUI:</span> {allergy.rxcui ?? t("common.notRecorded")}</p><div className="flex gap-2"><Button asChild variant="outline"><Link href={`/allergies/${allergy.id}/edit`}><Pencil className="size-4" />{t("common.edit")}</Link></Button><DeleteAllergy allergy={allergy} /></div></CardContent></Card>)}</div></>}</>;
}
