import type { ReactNode } from "react";

import { ApplicationNotice } from "@/components/application-notice";

export function AuthShell({ children }: { children: ReactNode }) {
  return <main className="mx-auto flex min-h-screen w-full max-w-lg flex-col justify-center gap-6 px-4 py-10"><header className="text-center"><p className="text-sm font-semibold uppercase tracking-[0.2em] text-primary">Pathergy</p><h1 className="mt-2 text-3xl font-bold">Personal health, clearly managed</h1></header>{children}<ApplicationNotice /></main>;
}
