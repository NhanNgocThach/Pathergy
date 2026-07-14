import type { ComponentType, ReactNode, SVGProps } from "react";

export function EmptyState({ title, description, action, icon: Icon }: { title: string; description: string; action?: ReactNode; icon?: ComponentType<SVGProps<SVGSVGElement>> }) {
  return <div className="rounded-lg border border-dashed bg-card p-8 text-center">{Icon ? <Icon className="mx-auto mb-3 size-8 text-muted-foreground" aria-hidden="true" /> : null}<h2 className="font-semibold">{title}</h2><p className="mt-2 text-sm text-muted-foreground">{description}</p>{action ? <div className="mt-4">{action}</div> : null}</div>;
}
