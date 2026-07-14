import type { Metadata } from "next";

import { LoginForm } from "@/features/auth/components/login-form";
import { GuestGuard } from "@/features/auth/guest-guard";

export const metadata: Metadata = { title: "Log in" };

export default async function LoginPage({ searchParams }: { searchParams: Promise<{ returnTo?: string }> }) {
  const { returnTo } = await searchParams;
  return <GuestGuard><LoginForm returnTo={returnTo} /></GuestGuard>;
}
