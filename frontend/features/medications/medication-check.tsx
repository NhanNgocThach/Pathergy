"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Search } from "lucide-react";
import { useRouter } from "next/navigation";
import * as React from "react";
import { Controller, useForm } from "react-hook-form";

import { ErrorMessage } from "@/components/error-message";
import { FormField } from "@/components/form-field";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { ProfileSelector } from "@/features/profiles/profile-selector";
import { MedicationAutocomplete } from "@/features/medications/medication-autocomplete";
import { useProfile } from "@/hooks/use-profile";
import { useI18n } from "@/i18n/i18n-provider";
import { queryKeys } from "@/lib/query-keys";
import { medicationSchema, type MedicationValues } from "@/schemas/health";
import { medicationService } from "@/services/health-service";
import type { MedicationSearchResult } from "@/types/health";

export function MedicationCheck() {
  const { t } = useI18n();
  const { selected, selectedPatientId } = useProfile();
  const router = useRouter();
  const client = useQueryClient();
  const [error, setError] = React.useState<string | null>(null);
  const [reference, setReference] = React.useState<MedicationSearchResult | null>(null);
  const form = useForm<MedicationValues>({
    resolver: zodResolver(medicationSchema),
    defaultValues: { medication_name: "" },
  });
  const check = useMutation({
    mutationFn: (values: MedicationValues) => medicationService.check(selectedPatientId!, values),
    onSuccess: (result) => {
      client.removeQueries({ queryKey: ["medication-result"] });
      client.setQueryData(queryKeys.medicationResult(result.history_id), result);
      void client.invalidateQueries({ queryKey: queryKeys.history(result.patient_id) });
      router.push(`/medication-check/results?id=${result.history_id}`);
    },
    onError: (caught: Error) => setError(caught.message),
  });
  const search = useMutation({
    mutationFn: (name: string) => medicationService.search(name),
    onSuccess: setReference,
    onError: (caught: Error) => setError(caught.message),
  });
  const submit = form.handleSubmit((values) => {
    setError(null);
    setReference(null);
    check.mutate(values);
  });

  async function searchReference() {
    const valid = await form.trigger();
    if (valid) {
      setError(null);
      setReference(null);
      search.mutate(form.getValues("medication_name"));
    }
  }

  return <>
    <PageHeader title={t("medication.title")} description={t("medication.description")} />
    <ProfileSelector label={t("profile.checkFor")} />
    <Card>
      <CardContent className="pt-6">
        <form noValidate className="space-y-5" onSubmit={submit}>
          {error ? <ErrorMessage title={t("medication.unavailable")} message={error} /> : null}
          <FormField
            id="medication_name"
            label={t("medication.name")}
            hint={t("medication.hint")}
            error={form.formState.errors.medication_name?.message}
          >
            <Controller
              control={form.control}
              name="medication_name"
              render={({ field }) => <MedicationAutocomplete
                id="medication_name"
                value={field.value}
                onChange={field.onChange}
                onBlur={field.onBlur}
                inputRef={field.ref}
                describedBy={`medication_name-hint${form.formState.errors.medication_name ? " medication_name-error" : ""}`}
                invalid={Boolean(form.formState.errors.medication_name)}
              />}
            />
          </FormField>
          <p className="text-sm text-muted-foreground">{t("medication.selectedPerson", { name: `${selected?.first_name ?? ""} ${selected?.last_name ?? ""}`.trim() })}</p>
          <div className="flex flex-wrap gap-3">
            <Button type="submit" disabled={!selectedPatientId || check.isPending || search.isPending}>{check.isPending ? t("medication.checking") : t("medication.check")}</Button>
            <Button type="button" variant="outline" disabled={check.isPending || search.isPending} onClick={() => void searchReference()}><Search className="size-4" />{search.isPending ? t("medication.searching") : t("medication.viewIngredients")}</Button>
          </div>
          <div className="sr-only" aria-live="polite">{check.isPending ? t("medication.checkingLive") : search.isPending ? t("medication.searchingLive") : ""}</div>
        </form>
      </CardContent>
    </Card>
    {reference ? <Card>
      <CardContent className="space-y-4 pt-6">
        <div><p className="text-sm text-muted-foreground">{t("medication.normalizedRxnorm")}</p><h2 className="text-xl font-bold">{reference.normalized_name}</h2><p className="text-sm">{t("medication.rxcui")}: {reference.rxcui}</p></div>
        <div><h3 className="font-semibold">{t("medication.ingredients")}</h3>{reference.active_ingredients.length ? <ul className="mt-2 list-disc space-y-1 pl-5">{reference.active_ingredients.map((ingredient) => <li key={ingredient.rxcui}>{ingredient.name} <span className="text-sm text-muted-foreground">(RxCUI {ingredient.rxcui})</span></li>)}</ul> : <p className="mt-2">{t("medication.ingredientInfoUnconfirmed")}</p>}</div>
        {!reference.ingredient_data_complete ? <p className="rounded-md bg-[#fef0c7] p-3 text-sm font-medium">{t("medication.incomplete")}</p> : null}
        <p className="text-sm text-muted-foreground">{t("notice.medicationDisclaimer")}</p>
      </CardContent>
    </Card> : null}
  </>;
}
