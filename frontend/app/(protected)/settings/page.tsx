import type { Metadata } from "next";
import { AccountSettings } from "@/features/account/account-settings";
export const metadata: Metadata = { title: "Account Settings" };
export default function SettingsPage() { return <AccountSettings />; }
