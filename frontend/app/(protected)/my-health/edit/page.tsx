import type { Metadata } from "next";
import { ProfileEdit } from "@/features/patients/profile-edit";
export const metadata: Metadata = { title: "Edit health profile" };
export default function EditHealthPage() { return <ProfileEdit />; }
