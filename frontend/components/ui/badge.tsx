import * as React from "react";

import { cn } from "@/lib/utils";

export function Badge({ className, variant = "secondary", ...props }: React.ComponentProps<"span"> & { variant?: "secondary" | "outline" | "destructive" }) {
  return <span className={cn("inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold", variant === "secondary" && "bg-secondary text-secondary-foreground", variant === "outline" && "border bg-card text-foreground", variant === "destructive" && "bg-[#fef3f2] text-destructive ring-1 ring-destructive/30", className)} {...props} />;
}
