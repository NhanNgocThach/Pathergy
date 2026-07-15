"use client";
import { useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { EmptyState } from "@/components/empty-state";
import { MedicationResultPanel } from "@/features/medications/medication-result-panel";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useI18n } from "@/i18n/i18n-provider";
import { queryKeys } from "@/lib/query-keys";
import type { MedicationCheckResult } from "@/types/health";
export function MedicationResults({ historyId }: { historyId: number }) { const { t } = useI18n(); const client = useQueryClient(); const result = Number.isInteger(historyId) ? client.getQueryData<MedicationCheckResult>(queryKeys.medicationResult(historyId)) : undefined; if (!result) return <><PageHeader title={t("medication.resultTitle")} /><EmptyState title={t("medication.detailsGone")} description={t("medication.detailsGoneDescription")} action={<div className="flex justify-center gap-3"><Button asChild><Link href="/medication-check">{t("medication.runCheck")}</Link></Button><Button asChild variant="outline"><Link href="/screening-history">{t("dashboard.viewHistory")}</Link></Button></div>} /></>; return <><PageHeader title={t("medication.resultTitle")} description={t("medication.resultFor", { medication: result.medication_query })} /><Card><CardContent className="space-y-4 pt-6"><div><p className="text-sm text-muted-foreground">{t("medication.normalized")}</p><h2 className="text-xl font-bold">{result.normalized_medication_name ?? t("common.notConfirmed")}</h2><p className="text-sm">{t("medication.rxcui")}: {result.medication_rxcui ?? t("common.notConfirmed")}</p></div><div><h3 className="font-semibold">{t("medication.ingredients")}</h3>{result.active_ingredients.length ? <ul className="mt-2 list-disc pl-5">{result.active_ingredients.map((ingredient) => <li key={ingredient.rxcui}>{ingredient.name} (RxCUI {ingredient.rxcui})</li>)}</ul> : <p className="mt-2">{t("medication.ingredientsUnconfirmed")}</p>}</div></CardContent></Card><MedicationResultPanel result={result} /><div className="flex flex-wrap gap-3"><Button asChild><Link href="/medication-check">{t("medication.checkAnother")}</Link></Button><Button asChild variant="outline"><Link href="/screening-history">{t("medication.viewHistory")}</Link></Button></div></>;
}
