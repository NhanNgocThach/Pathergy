import * as React from "react";

import { cn } from "@/lib/utils";

export function Alert({ className, variant = "default", ...props }: React.ComponentProps<"div"> & { variant?: "default" | "destructive" | "warning" }) {
  return <div role="alert" className={cn("rounded-md border bg-card p-4 text-sm leading-5", variant === "destructive" && "border-[#f4a7a1] bg-[#fef3f2] text-[#8f1c13]", variant === "warning" && "border-[#f3c875] bg-[#fef0c7] text-[#673708]", className)} {...props} />;
}
export function AlertTitle({ className, ...props }: React.ComponentProps<"h3">) { return <h3 className={cn("mb-1 font-semibold", className)} {...props} />; }
export function AlertDescription({ className, ...props }: React.ComponentProps<"div">) { return <div className={cn("text-sm", className)} {...props} />; }
