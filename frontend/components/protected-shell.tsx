"use client";

import { Activity, Clock3, HeartPulse, Home, KeyRound, LogOut, Menu, Pill, Settings, ShieldCheck, Users, X } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import * as React from "react";
import type { ReactNode } from "react";

import { ApplicationNotice } from "@/components/application-notice";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/use-auth";
import { cn } from "@/lib/utils";

const navigation = [
  { href: "/app", label: "Dashboard", icon: Home },
  { href: "/my-health", label: "My Health", icon: HeartPulse },
  { href: "/allergies", label: "Allergies", icon: Activity },
  { href: "/medication-check", label: "Medication Check", icon: Pill },
  { href: "/screening-history", label: "Screening History", icon: Clock3 },
  { href: "/families", label: "Families", icon: Users },
  { href: "/security/sessions", label: "Security", icon: ShieldCheck },
  { href: "/settings", label: "Account Settings", icon: Settings },
];

const mobilePrimary = navigation.slice(0, 1).concat(navigation.slice(1, 2), navigation.slice(3, 4), navigation.slice(5, 6));

function isCurrent(pathname: string, href: string) {
  return pathname === href || (href !== "/app" && pathname.startsWith(`${href}/`));
}

function NavLink({ href, label, icon: Icon, pathname, compact = false, onClick }: (typeof navigation)[number] & { pathname: string; compact?: boolean; onClick?: () => void }) {
  const active = isCurrent(pathname, href);
  return <Link href={href} onClick={onClick} aria-current={active ? "page" : undefined} className={cn("flex min-h-11 items-center gap-3 rounded-md px-3 py-2 text-sm font-semibold text-[var(--muted-foreground)] hover:bg-muted hover:text-foreground aria-[current=page]:bg-secondary aria-[current=page]:text-primary", compact && "flex-col justify-center gap-1 px-2 text-[11px]")}><Icon className="size-5 shrink-0" aria-hidden="true" />{label}</Link>;
}

export function ProtectedShell({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [moreOpen, setMoreOpen] = React.useState(false);

  async function handleLogout() { await logout(); router.replace("/login"); }

  return <div className="min-h-screen pb-20 lg:grid lg:grid-cols-[280px_1fr] lg:pb-0">
    <aside className="hidden border-r bg-card lg:sticky lg:top-0 lg:flex lg:h-screen lg:flex-col lg:p-6">
      <div className="mb-7"><p className="text-xl font-bold text-primary">Pathergy</p><p className="text-xs font-medium text-muted-foreground">Educational prototype</p></div>
      <nav aria-label="Application navigation" className="flex flex-1 flex-col gap-1">{navigation.map((item) => <NavLink key={item.href} {...item} pathname={pathname} />)}</nav>
      <div className="border-t pt-4"><p className="truncate text-sm font-semibold">{user?.display_name}</p><p className="truncate text-xs text-muted-foreground">{user?.email}</p><Button variant="outline" className="mt-4 w-full" onClick={() => void handleLogout()}><LogOut className="size-4" aria-hidden="true" />Log out</Button></div>
    </aside>
    <div className="min-w-0">
      <header className="sticky top-0 z-30 flex min-h-14 items-center justify-between border-b bg-card/95 px-4 backdrop-blur lg:hidden"><Link href="/app" className="font-bold text-primary">Pathergy</Link><p className="max-w-[55%] truncate text-sm font-medium">{user?.display_name}</p></header>
      <main id="main-content" tabIndex={-1} className="mx-auto w-full max-w-[1200px] space-y-8 p-4 py-6 sm:p-8"><ApplicationNotice />{children}</main>
    </div>
    <nav aria-label="Mobile navigation" className="fixed inset-x-0 bottom-0 z-40 grid grid-cols-5 border-t bg-card px-1 pb-[env(safe-area-inset-bottom)] lg:hidden">{mobilePrimary.map((item) => <NavLink key={item.href} {...item} pathname={pathname} compact />)}<button type="button" aria-expanded={moreOpen} aria-controls="mobile-more-menu" onClick={() => setMoreOpen((value) => !value)} className="flex min-h-14 flex-col items-center justify-center gap-1 rounded-md px-2 text-[11px] font-semibold text-muted-foreground"><Menu className="size-5" aria-hidden="true" />More</button></nav>
    {moreOpen ? <div className="fixed inset-0 z-50 bg-black/40 lg:hidden" onMouseDown={(event) => { if (event.target === event.currentTarget) setMoreOpen(false); }}><section id="mobile-more-menu" role="dialog" aria-modal="true" aria-labelledby="mobile-more-title" className="absolute inset-x-0 bottom-0 rounded-t-2xl bg-card p-4 pb-[calc(1rem+env(safe-area-inset-bottom))]"><div className="mb-3 flex items-center justify-between"><h2 id="mobile-more-title" className="text-lg font-bold">More</h2><Button variant="ghost" size="icon" aria-label="Close menu" onClick={() => setMoreOpen(false)}><X className="size-5" /></Button></div><nav className="grid gap-1">{navigation.filter((item) => !mobilePrimary.some((primary) => primary.href === item.href)).map((item) => <NavLink key={item.href} {...item} pathname={pathname} onClick={() => setMoreOpen(false)} />)}<Link href="/change-password" onClick={() => setMoreOpen(false)} className="flex min-h-11 items-center gap-3 rounded-md px-3 text-sm font-semibold hover:bg-muted"><KeyRound className="size-5" />Change password</Link><Button variant="outline" className="mt-2 justify-start" onClick={() => void handleLogout()}><LogOut className="size-5" />Log out</Button></nav></section></div> : null}
  </div>;
}
