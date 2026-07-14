import type { ReactNode } from "react";

import { ProtectedShell } from "@/components/protected-shell";
import { AuthGuard } from "@/features/auth/auth-guard";
import { ProfileProvider } from "@/features/profiles/profile-provider";

export default function ProtectedLayout({ children }: { children: ReactNode }) {
  return <AuthGuard><ProfileProvider><ProtectedShell>{children}</ProtectedShell></ProfileProvider></AuthGuard>;
}
