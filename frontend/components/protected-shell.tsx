"use client";

import { Activity, Clock3, HeartPulse, Home, KeyRound, LogOut, Menu, Pill, Settings, ShieldCheck, Users, X } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import * as React from "react";
import type { ReactNode } from "react";

import { ApplicationNotice } from "@/components/application-notice";
import { LanguageSelector } from "@/components/language-selector";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/use-auth";
import { useI18n } from "@/i18n/i18n-provider";
import { cn } from "@/lib/utils";

const navigation = [
  { href: "/app", labelKey: "nav.dashboard", icon: Home },
  { href: "/my-health", labelKey: "nav.health", icon: HeartPulse },
  { href: "/allergies", labelKey: "nav.allergies", icon: Activity },
  { href: "/medication-check", labelKey: "nav.medication", icon: Pill },
  { href: "/screening-history", labelKey: "nav.history", icon: Clock3 },
  { href: "/families", labelKey: "nav.families", icon: Users },
  { href: "/security/sessions", labelKey: "nav.security", icon: ShieldCheck },
  { href: "/settings", labelKey: "nav.settings", icon: Settings },
];

const mobilePrimary = navigation.slice(0, 1).concat(navigation.slice(1, 2), navigation.slice(3, 4), navigation.slice(5, 6));

function isCurrent(pathname: string, href: string) {
  return pathname === href || (href !== "/app" && pathname.startsWith(`${href}/`));
}

function NavLink({ href, labelKey, icon: Icon, pathname, compact = false, onClick }: (typeof navigation)[number] & { pathname: string; compact?: boolean; onClick?: () => void }) {
  const { t } = useI18n();
  const active = isCurrent(pathname, href);
  return <Link href={href} onClick={onClick} aria-current={active ? "page" : undefined} className={cn("flex min-h-11 items-center gap-3 rounded-md px-3 py-2 text-sm font-semibold text-[var(--muted-foreground)] hover:bg-muted hover:text-foreground aria-[current=page]:bg-secondary aria-[current=page]:text-primary", compact && "flex-col justify-center gap-1 px-2 text-[11px]")}><Icon className="size-5 shrink-0" aria-hidden="true" />{t(labelKey)}</Link>;
}

export function ProtectedShell({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const { t } = useI18n();
  const [moreOpen, setMoreOpen] = React.useState(false);

  async function handleLogout() { await logout(); router.replace("/login"); }

  return <div className="min-h-screen pb-20 lg:grid lg:grid-cols-[280px_1fr] lg:pb-0">
    <aside className="hidden border-r bg-card lg:sticky lg:top-0 lg:flex lg:h-screen lg:flex-col lg:p-6">
      <div className="mb-5"><p className="text-xl font-bold text-primary">Pathergy</p><p className="text-xs font-medium text-muted-foreground">{t("brand.prototype")}</p></div>
      <LanguageSelector compact />
      <nav aria-label={t("nav.application")} className="mt-4 flex flex-1 flex-col gap-1">{navigation.map((item) => <NavLink key={item.href} {...item} pathname={pathname} />)}</nav>
      <div className="border-t pt-4"><p className="truncate text-sm font-semibold">{user?.display_name}</p><p className="truncate text-xs text-muted-foreground">{user?.email}</p><Button variant="outline" className="mt-4 w-full" onClick={() => void handleLogout()}><LogOut className="size-4" aria-hidden="true" />{t("auth.logout")}</Button></div>
    </aside>
    <div className="min-w-0">
      <header className="sticky top-0 z-30 flex min-h-14 items-center justify-between gap-2 border-b bg-card/95 px-4 backdrop-blur lg:hidden"><Link href="/app" className="font-bold text-primary">Pathergy</Link><LanguageSelector compact /></header>
      <main id="main-content" tabIndex={-1} className="mx-auto w-full max-w-[1200px] space-y-8 p-4 py-6 sm:p-8"><ApplicationNotice />{children}</main>
    </div>
    <nav aria-label={t("nav.mobile")} className="fixed inset-x-0 bottom-0 z-40 grid grid-cols-5 border-t bg-card px-1 pb-[env(safe-area-inset-bottom)] lg:hidden">{mobilePrimary.map((item) => <NavLink key={item.href} {...item} pathname={pathname} compact />)}<button type="button" aria-expanded={moreOpen} aria-controls="mobile-more-menu" onClick={() => setMoreOpen((value) => !value)} className="flex min-h-14 flex-col items-center justify-center gap-1 rounded-md px-2 text-[11px] font-semibold text-muted-foreground"><Menu className="size-5" aria-hidden="true" />{t("nav.more")}</button></nav>
    {moreOpen ? <div className="fixed inset-0 z-50 bg-black/40 lg:hidden" onMouseDown={(event) => { if (event.target === event.currentTarget) setMoreOpen(false); }}><section id="mobile-more-menu" role="dialog" aria-modal="true" aria-labelledby="mobile-more-title" className="absolute inset-x-0 bottom-0 rounded-t-2xl bg-card p-4 pb-[calc(1rem+env(safe-area-inset-bottom))]"><div className="mb-3 flex items-center justify-between"><h2 id="mobile-more-title" className="text-lg font-bold">{t("nav.more")}</h2><Button variant="ghost" size="icon" aria-label={t("nav.close")} onClick={() => setMoreOpen(false)}><X className="size-5" /></Button></div><nav className="grid gap-1">{navigation.filter((item) => !mobilePrimary.some((primary) => primary.href === item.href)).map((item) => <NavLink key={item.href} {...item} pathname={pathname} onClick={() => setMoreOpen(false)} />)}<Link href="/change-password" onClick={() => setMoreOpen(false)} className="flex min-h-11 items-center gap-3 rounded-md px-3 text-sm font-semibold hover:bg-muted"><KeyRound className="size-5" />{t("auth.changePassword")}</Link><Button variant="outline" className="mt-2 justify-start" onClick={() => void handleLogout()}><LogOut className="size-5" />{t("auth.logout")}</Button></nav></section></div> : null}
  </div>;
}
