import type { Metadata } from "next";
import { ProfileView } from "@/features/patients/profile-view";
export const metadata: Metadata = { title: "My Health" };
export default function MyHealthPage() { return <ProfileView />; }
