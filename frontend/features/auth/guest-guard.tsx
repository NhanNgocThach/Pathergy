"use client";

import { useRouter } from "next/navigation";
import * as React from "react";

import { Spinner } from "@/components/spinner";
import { useAuth } from "@/hooks/use-auth";

export function GuestGuard({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  React.useEffect(() => {
    if (!isLoading && user) router.replace("/app");
  }, [isLoading, router, user]);

  if (isLoading || user) return <Spinner label="Checking your session" />;
  return children;
}
