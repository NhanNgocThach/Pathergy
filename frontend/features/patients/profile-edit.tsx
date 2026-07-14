"use client";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
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
import { ProfileSelector } from "@/features/profiles/profile-selector";
import { useProfile } from "@/hooks/use-profile";
import { queryKeys } from "@/lib/query-keys";
import { patientSchema, type PatientValues } from "@/schemas/health";
import { patientService } from "@/services/health-service";

function ProfileForm({ patientId, values }: { patientId: number; values: PatientValues }) { const router = useRouter(); const client = useQueryClient(); const [error, setError] = React.useState<string | null>(null); const form = useForm<PatientValues>({ resolver: zodResolver(patientSchema), defaultValues: values }); const mutation = useMutation({ mutationFn: (data: PatientValues) => patientService.update(patientId, data), onSuccess: (updated) => { client.setQueryData(queryKeys.patient(patientId), updated); void client.invalidateQueries({ queryKey: queryKeys.patients }); router.push("/my-health"); }, onError: (caught: Error) => setError(caught.message) }); return <Card><CardContent className="pt-6"><form noValidate className="space-y-5" onSubmit={form.handleSubmit((data) => { setError(null); mutation.mutate(data); })}>{error ? <ErrorMessage title="Profile was not updated" message={error} /> : null}<FormField id="first_name" label="First name" error={form.formState.errors.first_name?.message}><Input id="first_name" autoComplete="given-name" {...form.register("first_name")} /></FormField><FormField id="last_name" label="Last name" error={form.formState.errors.last_name?.message}><Input id="last_name" autoComplete="family-name" {...form.register("last_name")} /></FormField><FormField id="date_of_birth" label="Date of birth" error={form.formState.errors.date_of_birth?.message}><Input id="date_of_birth" type="date" {...form.register("date_of_birth")} /></FormField><div className="flex flex-wrap gap-3"><Button type="submit" disabled={mutation.isPending}>{mutation.isPending ? "Saving…" : "Save profile"}</Button><Button asChild variant="outline"><Link href="/my-health">Cancel</Link></Button></div></form></CardContent></Card>; }
export function ProfileEdit() { const { selectedPatientId } = useProfile(); const query = useQuery({ queryKey: queryKeys.patient(selectedPatientId!), queryFn: () => patientService.get(selectedPatientId!), enabled: Boolean(selectedPatientId) }); return <><PageHeader title="Edit health profile" description="Only the fields supported by the backend can be changed." /><ProfileSelector />{query.isLoading ? <p role="status">Loading profile…</p> : query.error ? <ErrorMessage message={query.error.message} /> : query.data ? <ProfileForm key={query.data.id} patientId={query.data.id} values={{ first_name: query.data.first_name, last_name: query.data.last_name, date_of_birth: query.data.date_of_birth }} /> : null}</>; }
