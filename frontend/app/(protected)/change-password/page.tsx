import type { Metadata } from "next";

import { PageHeader } from "@/components/page-header";
import { ChangePasswordForm } from "@/features/auth/components/change-password-form";

export const metadata: Metadata = { title: "Change password" };
export default function ChangePasswordPage() { return <><PageHeader title="Change password" description="Changing your password revokes every active session." /><div className="max-w-xl"><ChangePasswordForm /></div></>; }
