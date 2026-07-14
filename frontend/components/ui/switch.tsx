import * as React from "react";

export function Switch({ label, ...props }: Omit<React.ComponentProps<"input">, "type"> & { label: string }) {
  return <label className="flex min-h-11 items-center justify-between gap-4"><span className="text-sm font-medium">{label}</span><input type="checkbox" role="switch" className="size-5 accent-[var(--primary)]" {...props} /></label>;
}
