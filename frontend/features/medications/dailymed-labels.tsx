"use client";

import { ExternalLink } from "lucide-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { useI18n } from "@/i18n/i18n-provider";
import type { MedicationDetailsResult } from "@/types/health";


export function DailyMedLabels({ details }: { details: MedicationDetailsResult }) {
  const { t } = useI18n();
  const { dailymed } = details;

  return <div className="space-y-3">
    <div>
      <h3 className="font-semibold">{t("medication.officialLabels")}</h3>
      <p className="mt-1 text-sm text-muted-foreground">{t("medication.labelsDescription")}</p>
    </div>

    {dailymed.labels.length ? <ul className="space-y-3">
      {dailymed.labels.map((label) => <li key={label.set_id} className="rounded-md border p-4">
        <a className="font-semibold text-primary underline-offset-4 hover:underline" href={label.url} target="_blank" rel="noopener noreferrer">
          {label.title} <ExternalLink className="ml-1 inline size-4" aria-hidden="true" />
        </a>
        <p className="mt-2 text-sm text-muted-foreground">
          {t("medication.labelMetadata", { date: label.published_date, version: label.version })}
        </p>
      </li>)}
    </ul> : <Alert>
      <AlertTitle>{t(`medication.dailyMedStatus.${dailymed.status}`)}</AlertTitle>
      <AlertDescription>{t(`medication.dailyMedMessage.${dailymed.status}`)}</AlertDescription>
    </Alert>}

    {dailymed.status === "INCOMPLETE" && dailymed.labels.length ? <Alert>
      <AlertTitle>{t("medication.dailyMedStatus.INCOMPLETE")}</AlertTitle>
      <AlertDescription>{t("medication.dailyMedMessage.INCOMPLETE")}</AlertDescription>
    </Alert> : null}
    <p className="text-sm text-muted-foreground">{dailymed.disclaimer}</p>
  </div>;
}
