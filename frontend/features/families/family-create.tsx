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
import { useI18n } from "@/i18n/i18n-provider";
import { queryKeys } from "@/lib/query-keys";
import { familyGroupSchema, type FamilyGroupValues } from "@/schemas/family";
import { familyService } from "@/services/family-service";
export function FamilyCreate() { const { t } = useI18n(); const { user } = useAuth(); const router = useRouter(); const client = useQueryClient(); const [error, setError] = React.useState<string | null>(null); const form = useForm<FamilyGroupValues>({ resolver: zodResolver(familyGroupSchema), defaultValues: { name: "" } }); const mutation = useMutation({ mutationFn: familyService.create, onSuccess: (group) => { void client.invalidateQueries({ queryKey: queryKeys.families(user!.user_id) }); router.push(`/families/${group.family_group_id}`); }, onError: (caught: Error) => setError(caught.message) }); return <><PageHeader title={t("family.create")} description={t("family.createDescription")} /><Card className="max-w-xl"><CardContent className="pt-6"><form noValidate className="space-y-5" onSubmit={form.handleSubmit((values) => mutation.mutate(values))}>{error ? <ErrorMessage message={error} /> : null}<FormField id="name" label={t("family.name")} error={form.formState.errors.name?.message}><Input id="name" {...form.register("name")} /></FormField><div className="flex gap-3"><Button type="submit" disabled={mutation.isPending}>{mutation.isPending ? t("family.creating") : t("family.create")}</Button><Button asChild variant="outline"><Link href="/families">{t("common.cancel")}</Link></Button></div></form></CardContent></Card></>; }
