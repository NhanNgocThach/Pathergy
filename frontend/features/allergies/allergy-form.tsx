"use client";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useRouter } from "next/navigation";
import * as React from "react";
import { useForm, useWatch } from "react-hook-form";
import { ErrorMessage } from "@/components/error-message";
import { FormField } from "@/components/form-field";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { ProfileSelector } from "@/features/profiles/profile-selector";
import { useProfile } from "@/hooks/use-profile";
import { useI18n } from "@/i18n/i18n-provider";
import { queryKeys } from "@/lib/query-keys";
import { allergySchema, type AllergyValues } from "@/schemas/health";
import { allergyService } from "@/services/health-service";

function Form({ patientId, allergyId, initial }: { patientId: number; allergyId?: number; initial?: AllergyValues }) {
  const { t } = useI18n(); const router = useRouter(); const client = useQueryClient(); const [error, setError] = React.useState<string | null>(null); const form = useForm<AllergyValues>({ resolver: zodResolver(allergySchema), defaultValues: initial ?? { substance: "", rxcui: "", reaction: "", severity: "moderate" } }); const reaction = useWatch({ control: form.control, name: "reaction" });
  const mutation = useMutation({ mutationFn: (values: AllergyValues) => allergyId ? allergyService.update(patientId, allergyId, values) : allergyService.create(patientId, values), onSuccess: () => { void client.invalidateQueries({ queryKey: queryKeys.allergies(patientId) }); router.push("/allergies"); }, onError: (caught: Error) => setError(caught.message) });
  return <Card><CardContent className="pt-6"><form noValidate className="space-y-5" onSubmit={form.handleSubmit((values) => { setError(null); mutation.mutate(values); })}>{error ? <ErrorMessage title={t("allergy.notSaved")} message={error} /> : null}<FormField id="substance" label={t("allergy.substance")} hint={t("allergy.substanceHint")} error={form.formState.errors.substance?.message}><Input id="substance" {...form.register("substance")} /></FormField><FormField id="rxcui" label={t("allergy.rxcuiOptional")} hint={t("allergy.rxcuiHint")} error={form.formState.errors.rxcui?.message}><Input id="rxcui" inputMode="numeric" {...form.register("rxcui")} /></FormField><FormField id="reaction" label={t("allergy.reactionOptional")} hint={t("allergy.characters", { count: reaction.length })} error={form.formState.errors.reaction?.message}><Textarea id="reaction" maxLength={200} {...form.register("reaction")} /></FormField><FormField id="severity" label={t("allergy.severity")} error={form.formState.errors.severity?.message}><Select id="severity" {...form.register("severity")}><option value="mild">{t("severity.mild")}</option><option value="moderate">{t("severity.moderate")}</option><option value="severe">{t("severity.severe")}</option></Select></FormField><div className="flex flex-wrap gap-3"><Button type="submit" disabled={mutation.isPending}>{mutation.isPending ? t("common.saving") : allergyId ? t("allergy.saveChanges") : t("allergy.add")}</Button><Button asChild variant="outline"><Link href="/allergies">{t("common.cancel")}</Link></Button></div></form></CardContent></Card>;
}
export function AllergyCreate() { const { t } = useI18n(); const { selected, selectedPatientId } = useProfile(); return <><PageHeader title={t("allergy.add")} description={selected?.isOwn ? t("allergy.descriptionOwn") : t("allergy.descriptionShared")} /><ProfileSelector />{selectedPatientId ? <Form key={selectedPatientId} patientId={selectedPatientId} /> : null}</>; }
export function AllergyEdit({ allergyId }: { allergyId: number }) { const { t } = useI18n(); const { selectedPatientId } = useProfile(); const query = useQuery({ queryKey: queryKeys.allergy(selectedPatientId!, allergyId), queryFn: () => allergyService.get(selectedPatientId!, allergyId), enabled: Boolean(selectedPatientId && Number.isInteger(allergyId)) }); return <><PageHeader title={t("allergy.edit")} description={t("allergy.editDescription")} /><ProfileSelector />{query.isLoading ? <p role="status">{t("allergy.loadingOne")}</p> : query.error ? <ErrorMessage message={query.error.message} /> : query.data ? <Form key={`${selectedPatientId}-${allergyId}`} patientId={selectedPatientId!} allergyId={allergyId} initial={{ substance: query.data.substance, rxcui: query.data.rxcui ?? "", reaction: query.data.reaction ?? "", severity: query.data.severity }} /> : null}</>; }
