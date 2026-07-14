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
import { queryKeys } from "@/lib/query-keys";
import { allergySchema, type AllergyValues } from "@/schemas/health";
import { allergyService } from "@/services/health-service";

function Form({ patientId, allergyId, initial }: { patientId: number; allergyId?: number; initial?: AllergyValues }) { const router = useRouter(); const client = useQueryClient(); const [error, setError] = React.useState<string | null>(null); const form = useForm<AllergyValues>({ resolver: zodResolver(allergySchema), defaultValues: initial ?? { substance: "", rxcui: "", reaction: "", severity: "moderate" } }); const reaction = useWatch({ control: form.control, name: "reaction" }); const mutation = useMutation({ mutationFn: (values: AllergyValues) => allergyId ? allergyService.update(patientId, allergyId, values) : allergyService.create(patientId, values), onSuccess: () => { void client.invalidateQueries({ queryKey: queryKeys.allergies(patientId) }); router.push("/allergies"); }, onError: (caught: Error) => setError(caught.message) }); return <Card><CardContent className="pt-6"><form noValidate className="space-y-5" onSubmit={form.handleSubmit((values) => { setError(null); mutation.mutate(values); })}>{error ? <ErrorMessage title="Allergy record was not saved" message={error} /> : null}<FormField id="substance" label="Substance" hint="Use the ingredient or substance name from the person's existing record." error={form.formState.errors.substance?.message}><Input id="substance" {...form.register("substance")} /></FormField><FormField id="rxcui" label="RxCUI (optional)" hint="A numeric standardized RxNorm identifier. Leave blank if unknown." error={form.formState.errors.rxcui?.message}><Input id="rxcui" inputMode="numeric" {...form.register("rxcui")} /></FormField><FormField id="reaction" label="Reaction (optional)" hint={`${reaction.length}/200 characters`} error={form.formState.errors.reaction?.message}><Textarea id="reaction" maxLength={200} {...form.register("reaction")} /></FormField><FormField id="severity" label="Severity" error={form.formState.errors.severity?.message}><Select id="severity" {...form.register("severity")}><option value="mild">Mild</option><option value="moderate">Moderate</option><option value="severe">Severe</option></Select></FormField><div className="flex flex-wrap gap-3"><Button type="submit" disabled={mutation.isPending}>{mutation.isPending ? "Saving…" : allergyId ? "Save changes" : "Add allergy record"}</Button><Button asChild variant="outline"><Link href="/allergies">Cancel</Link></Button></div></form></CardContent></Card>; }
export function AllergyCreate() { const { selected, selectedPatientId } = useProfile(); return <><PageHeader title="Add allergy record" description={`Add a recorded substance for ${selected?.isOwn ? "your profile" : "the selected shared profile"}.`} /><ProfileSelector />{selectedPatientId ? <Form key={selectedPatientId} patientId={selectedPatientId} /> : null}</>; }
export function AllergyEdit({ allergyId }: { allergyId: number }) { const { selectedPatientId } = useProfile(); const query = useQuery({ queryKey: queryKeys.allergy(selectedPatientId!, allergyId), queryFn: () => allergyService.get(selectedPatientId!, allergyId), enabled: Boolean(selectedPatientId && Number.isInteger(allergyId)) }); return <><PageHeader title="Edit allergy record" description="The update sends every supported allergy field to the backend." /><ProfileSelector />{query.isLoading ? <p role="status">Loading allergy record…</p> : query.error ? <ErrorMessage message={query.error.message} /> : query.data ? <Form key={`${selectedPatientId}-${allergyId}`} patientId={selectedPatientId!} allergyId={allergyId} initial={{ substance: query.data.substance, rxcui: query.data.rxcui ?? "", reaction: query.data.reaction ?? "", severity: query.data.severity }} /> : null}</>; }
