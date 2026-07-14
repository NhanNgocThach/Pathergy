import * as React from "react";

export function RadioGroup({ legend, children }: { legend: string; children: React.ReactNode }) {
  return <fieldset className="space-y-3"><legend className="text-sm font-semibold">{legend}</legend>{children}</fieldset>;
}

export function RadioItem({ label, ...props }: Omit<React.ComponentProps<"input">, "type"> & { label: string }) {
  return <label className="flex min-h-11 items-center gap-3 rounded-md border bg-card px-3"><input type="radio" className="size-5 accent-[var(--primary)]" {...props} /><span>{label}</span></label>;
}
