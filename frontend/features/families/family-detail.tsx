"use client";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import * as React from "react";
import { ErrorState } from "@/components/feedback/error-state";
import { PageHeader } from "@/components/page-header";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { MemberManagement } from "@/features/families/member-management";
import { PermissionEditor } from "@/features/permissions/permission-editor";
import { useAuth } from "@/hooks/use-auth";
import { useI18n } from "@/i18n/i18n-provider";
import { queryKeys } from "@/lib/query-keys";
import { familyService } from "@/services/family-service";

export function FamilyDetail({ familyId }: { familyId: number }) {
  const { t } = useI18n(); const { user } = useAuth(); const client = useQueryClient();
  const group = useQuery({ queryKey: queryKeys.family(familyId), queryFn: () => familyService.get(familyId), enabled: Number.isInteger(familyId) && familyId > 0 });
  const members = useQuery({ queryKey: queryKeys.members(familyId), queryFn: () => familyService.members(familyId), enabled: group.isSuccess });
  const ownMembership = members.data?.find((member) => member.user_id === user!.user_id && member.status === "ACTIVE"); const canManage = ownMembership?.role === "OWNER" || ownMembership?.role === "ADMIN"; const [name, setName] = React.useState<string | null>(null);
  const rename = useMutation({ mutationFn: () => familyService.update(familyId, { name: name ?? group.data!.name }), onSuccess: (updated) => { client.setQueryData(queryKeys.family(familyId), updated); setName(null); void client.invalidateQueries({ queryKey: queryKeys.families(user!.user_id) }); } });
  const leave = useMutation({ mutationFn: () => familyService.leave(familyId, user!.user_id), onSuccess: () => { void client.invalidateQueries({ queryKey: queryKeys.families(user!.user_id) }); window.location.assign("/families"); } });
  if (group.isLoading) return <p role="status">{t("family.loading")}</p>;
  if (group.error) return <><PageHeader title={t("family.title")} /><ErrorState message={group.error.message} onRetry={() => void group.refetch()} /></>;
  return <><PageHeader title={group.data!.name} description={t("family.managementSeparate")} actions={<Button asChild variant="outline"><Link href="/families">{t("family.all")}</Link></Button>} /><div className="grid gap-4 md:grid-cols-3"><Card><CardContent className="pt-6"><p className="text-sm text-muted-foreground">{t("family.yourRole")}</p><p className="mt-1 text-xl font-bold">{ownMembership ? t(`role.${ownMembership.role}`) : t("common.notAvailable")}</p></CardContent></Card><Card><CardContent className="pt-6"><p className="text-sm text-muted-foreground">{t("family.membershipStatus")}</p><Badge className="mt-2">{ownMembership ? t(`status.${ownMembership.status}`) : t("common.notAvailable")}</Badge></CardContent></Card><Card><CardContent className="pt-6"><p className="text-sm text-muted-foreground">{t("family.relationship")}</p><p className="mt-1 text-xl font-bold">{ownMembership ? t(`relationship.${ownMembership.relationship}`) : t("common.notAvailable")}</p></CardContent></Card></div>
    {canManage ? <Card><CardHeader><CardTitle>{t("family.groupSettings")}</CardTitle></CardHeader><CardContent><label className="text-sm font-semibold" htmlFor="family-name">{t("family.name")}</label><div className="mt-2 flex flex-wrap gap-3"><Input id="family-name" className="max-w-md" value={name ?? group.data!.name} onChange={(event) => setName(event.target.value)} /><Button onClick={() => rename.mutate()} disabled={rename.isPending || !name?.trim()}>{t("family.saveName")}</Button></div>{rename.error ? <p role="alert" className="mt-2 text-sm text-destructive">{rename.error.message}</p> : null}</CardContent></Card> : null}
    {members.isLoading ? <p role="status">{t("family.loadingMembers")}</p> : members.error ? <ErrorState message={members.error.message} onRetry={() => void members.refetch()} /> : <MemberManagement groupId={familyId} members={members.data ?? []} canManage={canManage} currentUserId={user!.user_id} />}
    {ownMembership ? <PermissionEditor groupId={familyId} userId={user!.user_id} /> : null}
    {ownMembership ? <Card><CardHeader><CardTitle>{t("family.leaveTitle")}</CardTitle></CardHeader><CardContent><p className="mb-4 text-sm text-muted-foreground">{t("family.leaveDescription")}</p><AlertDialog><AlertDialogTrigger asChild><Button variant="destructive">{t("family.leaveTitle")}</Button></AlertDialogTrigger><AlertDialogContent><AlertDialogHeader><AlertDialogTitle>{t("family.leaveConfirm", { family: group.data!.name })}</AlertDialogTitle><AlertDialogDescription>{t("family.leaveConfirmDescription")}</AlertDialogDescription></AlertDialogHeader>{leave.error ? <p role="alert" className="text-sm text-destructive">{leave.error.message}</p> : null}<AlertDialogFooter><AlertDialogCancel>{t("common.cancel")}</AlertDialogCancel><AlertDialogAction onClick={(event) => { event.preventDefault(); leave.mutate(); }}>{t("family.leave")}</AlertDialogAction></AlertDialogFooter></AlertDialogContent></AlertDialog></CardContent></Card> : null}</>;
}
