import { Activity } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { Severity } from "@/types/health";
export function SeverityBadge({ severity }: { severity: Severity }) { return <Badge variant={severity === "severe" ? "destructive" : "outline"}><Activity className="mr-1 size-3.5" aria-hidden="true" />{severity[0].toUpperCase() + severity.slice(1)}</Badge>; }
