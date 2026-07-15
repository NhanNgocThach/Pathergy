"use client";

import { Activity } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { useI18n } from "@/i18n/i18n-provider";
import type { Severity } from "@/types/health";
export function SeverityBadge({ severity }: { severity: Severity }) { const { t } = useI18n(); return <Badge variant={severity === "severe" ? "destructive" : "outline"}><Activity className="mr-1 size-3.5" aria-hidden="true" />{t(`severity.${severity}`)}</Badge>; }
