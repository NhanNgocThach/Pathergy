import type { ReactNode } from "react";

import { Label } from "@/components/ui/label";

export function FormField({ id, label, hint, error, children }: { id: string; label: string; hint?: string; error?: string; children: ReactNode }) {
  return <div className="space-y-2"><Label htmlFor={id}>{label}</Label>{hint ? <p id={`${id}-hint`} className="text-sm text-muted-foreground">{hint}</p> : null}{children}{error ? <p id={`${id}-error`} className="text-sm font-medium text-destructive">{error}</p> : null}</div>;
}
