"use client";

import { CircleAlert, Info, TriangleAlert } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { useI18n } from "@/i18n/i18n-provider";
import type { MedicationCheckStatus } from "@/types/health";
export function ResultBadge({ result }: { result: MedicationCheckStatus }) { const { t } = useI18n(); const Icon = result === "POTENTIAL_ALLERGY_MATCH" ? CircleAlert : result === "UNABLE_TO_VERIFY" ? TriangleAlert : Info; return <Badge variant={result === "POTENTIAL_ALLERGY_MATCH" ? "destructive" : "secondary"}><Icon className="mr-1 size-3.5" aria-hidden="true" />{t(`result.${result}`)}</Badge>; }
