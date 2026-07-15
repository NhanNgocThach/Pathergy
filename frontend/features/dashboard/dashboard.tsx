"use client";

import { useQuery } from "@tanstack/react-query";
import { Activity, Clock3, HeartPulse, Pill, Plus, Users } from "lucide-react";
import Link from "next/link";

import { EmptyState } from "@/components/empty-state";
import { ErrorState } from "@/components/feedback/error-state";
import { ResultBadge } from "@/components/health/result-badge";
import { SeverityBadge } from "@/components/health/severity-badge";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useAuth } from "@/hooks/use-auth";
import { useI18n } from "@/i18n/i18n-provider";
import { formatDate, formatDateTime } from "@/lib/format";
import { queryKeys } from "@/lib/query-keys";
import { familyService } from "@/services/family-service";
import { allergyService, historyService, patientService } from "@/services/health-service";

function ModuleLoading() { const { t } = useI18n(); return <div role="status" aria-label={t("dashboard.loading")} className="space-y-3"><Skeleton className="w-2/3" /><Skeleton /><Skeleton className="w-5/6" /></div>; }

export function Dashboard() {
  const { user } = useAuth();
  const { t } = useI18n();
  const patientId = user!.patient_id;
  const profile = useQuery({ queryKey: queryKeys.patient(patientId), queryFn: () => patientService.get(patientId) });
  const allergies = useQuery({ queryKey: queryKeys.allergies(patientId), queryFn: () => allergyService.list(patientId) });
  const history = useQuery({ queryKey: queryKeys.history(patientId), queryFn: () => historyService.list(patientId) });
  const families = useQuery({ queryKey: queryKeys.families(user!.user_id), queryFn: () => familyService.listForUser(user!.user_id) });
  return <>
    <PageHeader title={t("dashboard.welcome", { name: user?.display_name ?? "Pathergy" })} description={t("dashboard.description")} />
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4"><Button asChild><Link href="/allergies/new"><Plus className="size-4" />{t("dashboard.addAllergy")}</Link></Button><Button asChild variant="secondary"><Link href="/medication-check"><Pill className="size-4" />{t("dashboard.checkMedication")}</Link></Button><Button asChild variant="outline"><Link href="/screening-history"><Clock3 className="size-4" />{t("dashboard.viewHistory")}</Link></Button><Button asChild variant="outline"><Link href="/families/new"><Users className="size-4" />{t("dashboard.createFamily")}</Link></Button></div>
    <div className="grid gap-6 lg:grid-cols-2">
      <Card><CardHeader><CardTitle className="flex items-center gap-2"><HeartPulse className="size-5" />{t("dashboard.profile")}</CardTitle></CardHeader><CardContent>{profile.isLoading ? <ModuleLoading /> : profile.error ? <ErrorState message={profile.error.message} onRetry={() => void profile.refetch()} /> : profile.data ? <dl className="grid gap-3"><div><dt className="text-sm text-muted-foreground">{t("dashboard.name")}</dt><dd className="font-semibold">{profile.data.first_name} {profile.data.last_name}</dd></div><div><dt className="text-sm text-muted-foreground">{t("dashboard.birthDate")}</dt><dd>{formatDate(profile.data.date_of_birth)}</dd></div><Button asChild variant="outline" className="mt-2 w-fit"><Link href="/my-health">{t("dashboard.viewProfile")}</Link></Button></dl> : null}</CardContent></Card>
      <Card><CardHeader><CardTitle className="flex items-center gap-2"><Activity className="size-5" />Known allergy records</CardTitle></CardHeader><CardContent>{allergies.isLoading ? <ModuleLoading /> : allergies.error ? <ErrorState message={allergies.error.message} onRetry={() => void allergies.refetch()} /> : allergies.data?.length ? <div className="space-y-3"><p className="text-3xl font-bold">{allergies.data.length}</p><ul className="space-y-2">{allergies.data.slice(0, 3).map((allergy) => <li key={allergy.id} className="flex items-center justify-between gap-3 rounded-md border p-3"><span className="font-medium">{allergy.substance}</span><SeverityBadge severity={allergy.severity} /></li>)}</ul><Button asChild variant="outline"><Link href="/allergies">View all records</Link></Button></div> : <EmptyState title="No allergy records" description="No allergy records have been added for your profile." action={<Button asChild><Link href="/allergies/new">Add allergy record</Link></Button>} />}</CardContent></Card>
      <Card><CardHeader><CardTitle className="flex items-center gap-2"><Clock3 className="size-5" />Recent medication checks</CardTitle></CardHeader><CardContent>{history.isLoading ? <ModuleLoading /> : history.error ? <ErrorState message={history.error.message} onRetry={() => void history.refetch()} /> : history.data?.length ? <ul className="space-y-3">{history.data.slice(0, 5).map((item) => <li key={item.id} className="space-y-1 border-b pb-3 last:border-0"><div className="flex flex-wrap items-center justify-between gap-2"><Link className="font-semibold underline-offset-4 hover:underline" href={`/screening-history/${item.id}`}>{item.medication_name}</Link><ResultBadge result={item.result} /></div><p className="text-xs text-muted-foreground">{formatDateTime(item.created_at)}</p></li>)}</ul> : <EmptyState title="No medication checks" description="No medication checks have been recorded for your profile." />}</CardContent></Card>
      <Card><CardHeader><CardTitle className="flex items-center gap-2"><Users className="size-5" />Family groups</CardTitle></CardHeader><CardContent>{families.isLoading ? <ModuleLoading /> : families.error ? <ErrorState message={families.error.message} onRetry={() => void families.refetch()} /> : families.data?.length ? <div className="space-y-3"><p><span className="text-3xl font-bold">{families.data.filter((item) => item.membership.status === "ACTIVE").length}</span> <span className="text-sm text-muted-foreground">active groups</span></p><ul className="space-y-2">{families.data.slice(0, 4).map(({ family_group: group, membership }) => <li key={membership.membership_id} className="rounded-md border p-3"><div className="flex justify-between gap-3"><span className="font-semibold">{group.name}</span><span className="text-xs font-semibold">{membership.status}</span></div><p className="text-sm text-muted-foreground">{membership.role} · {membership.relationship}</p></li>)}</ul><Button asChild variant="outline"><Link href="/families">View family groups</Link></Button></div> : <EmptyState title="No family groups" description="You have not joined or created a family group." action={<Button asChild><Link href="/families/new">Create family group</Link></Button>} />}</CardContent></Card>
    </div>
  </>;
}
