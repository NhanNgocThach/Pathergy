"use client";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import * as React from "react";
import { useForm } from "react-hook-form";
import { ErrorMessage } from "@/components/error-message";
import { FormField } from "@/components/form-field";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/hooks/use-auth";
import { queryKeys } from "@/lib/query-keys";
import { familyGroupSchema, type FamilyGroupValues } from "@/schemas/family";
import { familyService } from "@/services/family-service";
export function FamilyCreate() { const { user } = useAuth(); const router = useRouter(); const client = useQueryClient(); const [error, setError] = React.useState<string | null>(null); const form = useForm<FamilyGroupValues>({ resolver: zodResolver(familyGroupSchema), defaultValues: { name: "" } }); const mutation = useMutation({ mutationFn: familyService.create, onSuccess: (group) => { void client.invalidateQueries({ queryKey: queryKeys.families(user!.user_id) }); router.push(`/families/${group.family_group_id}`); }, onError: (caught: Error) => setError(caught.message) }); return <><PageHeader title="Create family group" description="The creator becomes an ACTIVE OWNER. This role manages the group, not other members' health information." /><Card className="max-w-xl"><CardContent className="pt-6"><form noValidate className="space-y-5" onSubmit={form.handleSubmit((values) => mutation.mutate(values))}>{error ? <ErrorMessage message={error} /> : null}<FormField id="name" label="Family group name" error={form.formState.errors.name?.message}><Input id="name" {...form.register("name")} /></FormField><div className="flex gap-3"><Button type="submit" disabled={mutation.isPending}>{mutation.isPending ? "Creating…" : "Create family group"}</Button><Button asChild variant="outline"><Link href="/families">Cancel</Link></Button></div></form></CardContent></Card></>; }
