import { AlertCircle, CircleAlert, Info, TriangleAlert } from "lucide-react";
import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

const styles = { info: "border-[#175cd3]/30 bg-[#eef4ff]", warning: "border-[#854a0e]/30 bg-[#fef0c7]", danger: "border-destructive/30 bg-[#fef3f2]", error: "border-destructive/30 bg-[#fef3f2]" };
const icons = { info: Info, warning: TriangleAlert, danger: CircleAlert, error: AlertCircle };
export function StatusPanel({ title, children, tone = "info", actions }: { title: string; children: ReactNode; tone?: keyof typeof styles; actions?: ReactNode }) { const Icon = icons[tone]; return <section role={tone === "error" ? "alert" : "status"} className={cn("rounded-xl border p-5", styles[tone])}><div className="flex items-start gap-3"><Icon className="mt-0.5 size-6 shrink-0" aria-hidden="true" /><div className="min-w-0 flex-1"><h2 className="text-lg font-bold">{title}</h2><div className="mt-2 space-y-2 text-sm leading-6">{children}</div>{actions ? <div className="mt-4 flex flex-wrap gap-3">{actions}</div> : null}</div></div></section>; }
