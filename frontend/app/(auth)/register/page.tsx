import type { Metadata } from "next";

import { RegisterForm } from "@/features/auth/components/register-form";
import { GuestGuard } from "@/features/auth/guest-guard";

export const metadata: Metadata = { title: "Create account" };
export default function RegisterPage() { return <GuestGuard><RegisterForm /></GuestGuard>; }
