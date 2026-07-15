"use client";
import { useQuery } from "@tanstack/react-query";
import { Plus, Users } from "lucide-react";
import Link from "next/link";
import { EmptyState } from "@/components/empty-state";
import { ErrorState } from "@/components/feedback/error-state";
import { PageHeader } from "@/components/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useAuth } from "@/hooks/use-auth";
import { useI18n } from "@/i18n/i18n-provider";
import { formatDate } from "@/lib/format";
import { queryKeys } from "@/lib/query-keys";
import { familyService } from "@/services/family-service";
export function FamilyList() { const { t } = useI18n(); const { user } = useAuth(); const query = useQuery({ queryKey: queryKeys.families(user!.user_id), queryFn: () => familyService.listForUser(user!.user_id) }); const items = [...(query.data ?? [])].sort((a, b) => Number(b.membership.status === "ACTIVE") - Number(a.membership.status === "ACTIVE") || b.membership.membership_id - a.membership.membership_id); return <><PageHeader title={t("family.title")} description={t("family.description")} actions={<Button asChild><Link href="/families/new"><Plus className="size-4" />{t("family.create")}</Link></Button>} />{query.isLoading ? <p role="status">{t("family.loading")}</p> : query.error ? <ErrorState message={query.error.message} onRetry={() => void query.refetch()} /> : !items.length ? <EmptyState icon={Users} title={t("family.empty")} description={t("family.emptyDescription")} action={<Button asChild><Link href="/families/new">{t("family.create")}</Link></Button>} /> : <div className="grid gap-4 md:grid-cols-2">{items.map(({ family_group: group, membership }) => <Card key={membership.membership_id}><CardContent className="space-y-4 pt-6"><div className="flex items-start justify-between gap-3"><div><h2 className="text-xl font-bold">{group.name}</h2><p className="text-sm text-muted-foreground">{t("family.number", { id: group.family_group_id })}</p></div><Badge variant={membership.status === "ACTIVE" ? "secondary" : "outline"}>{t(`status.${membership.status}`)}</Badge></div><dl className="grid grid-cols-2 gap-3 text-sm"><div><dt className="text-muted-foreground">{t("family.yourRole")}</dt><dd className="font-semibold">{t(`role.${membership.role}`)}</dd></div><div><dt className="text-muted-foreground">{t("family.relationship")}</dt><dd className="font-semibold">{t(`relationship.${membership.relationship}`)}</dd></div><div><dt className="text-muted-foreground">{t("family.joined")}</dt><dd>{formatDate(membership.joined_at)}</dd></div>{membership.left_at ? <div><dt className="text-muted-foreground">{t("family.leftClosed")}</dt><dd>{formatDate(membership.left_at)}</dd></div> : null}</dl>{membership.status === "ACTIVE" ? <Button asChild variant="outline"><Link href={`/families/${group.family_group_id}`}>{t("family.view")}</Link></Button> : <p className="text-sm text-muted-foreground">{t("family.inactiveDescription")}</p>}</CardContent></Card>)}</div>}</>; }
