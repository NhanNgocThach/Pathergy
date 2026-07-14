import type { Metadata } from "next";

import { PageHeader } from "@/components/page-header";
import { SessionList } from "@/features/auth/components/session-list";

export const metadata: Metadata = { title: "Active sessions" };
export default function SessionsPage() { return <><PageHeader title="Active sessions" description="Review devices returned by the backend and revoke access when needed." /><SessionList /></>; }
