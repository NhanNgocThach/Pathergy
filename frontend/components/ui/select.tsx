import { ChevronDown } from "lucide-react";
import * as React from "react";
import { cn } from "@/lib/utils";

export function Select({ className, children, ...props }: React.ComponentProps<"select">) {
  return <div className="relative"><select className={cn("min-h-11 w-full appearance-none rounded-md border border-input bg-card px-3 py-2 pr-10 text-base shadow-sm disabled:opacity-60 aria-invalid:border-destructive md:text-sm", className)} {...props}>{children}</select><ChevronDown className="pointer-events-none absolute right-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" aria-hidden="true" /></div>;
}
