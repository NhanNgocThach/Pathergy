"use client";
import { useQuery } from "@tanstack/react-query";
import { Pencil } from "lucide-react";
import Link from "next/link";
import { ErrorState } from "@/components/feedback/error-state";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ProfileSelector } from "@/features/profiles/profile-selector";
import { useProfile } from "@/hooks/use-profile";
import { useI18n } from "@/i18n/i18n-provider";
import { formatDate, formatPersonName } from "@/lib/format";
import { queryKeys } from "@/lib/query-keys";
import { patientService } from "@/services/health-service";

export function ProfileView() {
  const { selected, selectedPatientId } = useProfile();
  const { locale, t } = useI18n();
  const query = useQuery({ queryKey: queryKeys.patient(selectedPatientId!), queryFn: () => patientService.get(selectedPatientId!), enabled: Boolean(selectedPatientId) });
  return <><PageHeader title={t("profile.title")} description={t("profile.description")} /><ProfileSelector />{query.isLoading ? <Skeleton className="h-48" /> : query.error ? <ErrorState message={query.error.message} onRetry={() => void query.refetch()} /> : query.data ? <Card><CardContent className="pt-6"><div className="mb-5 flex flex-wrap items-start justify-between gap-4"><div><p className="text-xs font-semibold uppercase tracking-wide text-primary">{selected?.isOwn ? t("profile.mine") : t("profile.shared")}</p><h2 className="mt-1 text-2xl font-bold">{formatPersonName(query.data.first_name, query.data.last_name, locale)}</h2>{selected?.familyGroupName ? <p className="text-sm text-muted-foreground">{t("profile.sharedThrough", { family: selected.familyGroupName, relationship: selected.relationship ?? "" })}</p> : null}</div><Button asChild variant="outline"><Link href="/my-health/edit"><Pencil className="size-4" />{t("profile.editFields")}</Link></Button></div><dl className="grid gap-4 sm:grid-cols-2"><div><dt className="text-sm text-muted-foreground">{t("profile.firstName")}</dt><dd className="font-semibold">{query.data.first_name}</dd></div><div><dt className="text-sm text-muted-foreground">{t("profile.lastName")}</dt><dd className="font-semibold">{query.data.last_name}</dd></div><div><dt className="text-sm text-muted-foreground">{t("profile.birthDate")}</dt><dd className="font-semibold">{formatDate(query.data.date_of_birth)}</dd></div></dl><div className="mt-6 rounded-md bg-secondary p-4 text-sm"><p className="font-semibold">{t("profile.ownership")}</p><p className="mt-1">{t("profile.ownershipDescription")}</p></div></CardContent></Card> : null}</>;
}
