"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { MonitorSmartphone } from "lucide-react";
import { useRouter } from "next/navigation";

import { EmptyState } from "@/components/empty-state";
import { ErrorMessage } from "@/components/error-message";
import { Spinner } from "@/components/spinner";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatDateTime } from "@/lib/format";
import { queryKeys } from "@/lib/query-keys";
import { tokenStore } from "@/lib/token-store";
import { authService } from "@/services/auth-service";
import type { AuthSession } from "@/types/auth";

function SessionCard({ session, onRevoke, isRevoking }: { session: AuthSession; onRevoke: () => void; isRevoking: boolean }) {
  return <Card><CardHeader className="flex-row items-start justify-between gap-4"><div><CardTitle className="flex items-center gap-2 text-lg"><MonitorSmartphone className="size-5" aria-hidden="true" />{session.device_name || session.device_type || "Unknown browser"}</CardTitle>{session.is_current ? <Badge className="mt-2">Current session</Badge> : null}</div><AlertDialog><AlertDialogTrigger asChild><Button variant="outline" size="sm">Revoke</Button></AlertDialogTrigger><AlertDialogContent><AlertDialogHeader><AlertDialogTitle>Revoke this session?</AlertDialogTitle><AlertDialogDescription>{session.is_current ? "This is your current session. Revoking it will return you to login." : "This device will need to log in again."}</AlertDialogDescription></AlertDialogHeader><AlertDialogFooter><AlertDialogCancel>Cancel</AlertDialogCancel><AlertDialogAction disabled={isRevoking} onClick={onRevoke}>{isRevoking ? "Revoking…" : "Revoke session"}</AlertDialogAction></AlertDialogFooter></AlertDialogContent></AlertDialog></CardHeader><CardContent><dl className="grid gap-3 text-sm sm:grid-cols-2"><div><dt className="font-semibold">Created</dt><dd>{formatDateTime(session.created_at)}</dd></div><div><dt className="font-semibold">Last used</dt><dd>{formatDateTime(session.last_used_at)}</dd></div><div><dt className="font-semibold">Expires</dt><dd>{formatDateTime(session.expires_at)}</dd></div>{session.ip_address ? <div><dt className="font-semibold">IP address</dt><dd>{session.ip_address}</dd></div> : null}{session.user_agent ? <div className="min-w-0 sm:col-span-2"><dt className="font-semibold">Browser details</dt><dd className="break-words text-muted-foreground">{session.user_agent}</dd></div> : null}</dl></CardContent></Card>;
}

export function SessionList() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const sessions = useQuery({ queryKey: queryKeys.sessions, queryFn: () => authService.listSessions() });
  const revokeOne = useMutation({ mutationFn: (session: AuthSession) => authService.revokeSession(session.session_id), onSuccess: async (_, session) => { if (session.is_current) { tokenStore.clear(); router.replace("/login"); return; } await queryClient.invalidateQueries({ queryKey: queryKeys.sessions }); } });
  const revokeAll = useMutation({ mutationFn: () => authService.revokeAllSessions(), onSuccess: () => { tokenStore.clear(); router.replace("/login"); } });
  if (sessions.isLoading) return <Spinner label="Loading active sessions" />;
  if (sessions.error) return <ErrorMessage title="Sessions unavailable" message={sessions.error.message} />;
  if (!sessions.data?.length) return <EmptyState title="No active sessions" description="No active device sessions were returned by the server." />;
  return <div className="space-y-4"><div className="flex justify-end"><AlertDialog><AlertDialogTrigger asChild><Button variant="destructive">Revoke all sessions</Button></AlertDialogTrigger><AlertDialogContent><AlertDialogHeader><AlertDialogTitle>Revoke all sessions?</AlertDialogTitle><AlertDialogDescription>Every device, including this one, will be signed out. The backend does not currently support “all other sessions.”</AlertDialogDescription></AlertDialogHeader><AlertDialogFooter><AlertDialogCancel>Cancel</AlertDialogCancel><AlertDialogAction disabled={revokeAll.isPending} onClick={() => revokeAll.mutate()}>{revokeAll.isPending ? "Revoking…" : "Revoke all and sign out"}</AlertDialogAction></AlertDialogFooter></AlertDialogContent></AlertDialog></div>{revokeOne.error || revokeAll.error ? <ErrorMessage message={(revokeOne.error ?? revokeAll.error)?.message ?? "Session revocation failed."} /> : null}<div className="space-y-4">{sessions.data.map((session) => <SessionCard key={session.session_id} session={session} isRevoking={revokeOne.isPending && revokeOne.variables?.session_id === session.session_id} onRevoke={() => revokeOne.mutate(session)} />)}</div></div>;
}
