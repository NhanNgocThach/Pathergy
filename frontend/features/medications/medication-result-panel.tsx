"use client";

import { StatusPanel } from "@/components/feedback/status-panel";
import { useI18n } from "@/i18n/i18n-provider";
import type { MedicationCheckResult } from "@/types/health";

export function MedicationResultPanel({ result }: { result: MedicationCheckResult }) {
  const { t } = useI18n();
  if (result.result === "POTENTIAL_ALLERGY_MATCH") return <StatusPanel tone="danger" title={t("result.POTENTIAL_ALLERGY_MATCH")}><p>{t("screen.potentialDescription")}</p><div className="space-y-3">{result.matches.map((match) => <div key={`${match.allergy_id}-${match.ingredient_rxcui}`} className="rounded-md border border-destructive/20 bg-card/70 p-3"><p><strong>{t("screen.recordedAllergy")}:</strong> {match.recorded_substance}</p><p><strong>{t("screen.activeIngredient")}:</strong> {match.ingredient_name}</p><details className="mt-2"><summary className="cursor-pointer text-sm font-semibold">{t("screen.technical")}</summary><p className="mt-1 text-sm">{t("screen.method", { method: match.match_method, ingredient: match.ingredient_rxcui, recorded: match.recorded_rxcui ? t("screen.recordedRxcui", { rxcui: match.recorded_rxcui }) : "" })}</p></details></div>)}</div><p className="font-semibold">{t("screen.professionalReview")}</p><p>{t("notice.medicationDisclaimer")}</p></StatusPanel>;
  if (result.result === "NO_RECORDED_MATCH_FOUND") return <StatusPanel tone="info" title={t("result.NO_RECORDED_MATCH_FOUND")}><p>{t("screen.noMatchDescription")}</p><p>{t("screen.reviewRecommended")}</p><p>{t("notice.medicationDisclaimer")}</p></StatusPanel>;
  return <StatusPanel tone="warning" title={t("result.UNABLE_TO_VERIFY")}><p>{t("screen.unableDescription")}</p><p>{t("screen.externalUnavailable")}</p><p>{t("notice.medicationDisclaimer")}</p></StatusPanel>;
}
