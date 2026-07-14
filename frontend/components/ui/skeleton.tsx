import { cn } from "@/lib/utils";
export function Skeleton({ className }: { className?: string }) { return <div className={cn("h-5 animate-pulse rounded bg-muted", className)} aria-hidden="true" />; }
