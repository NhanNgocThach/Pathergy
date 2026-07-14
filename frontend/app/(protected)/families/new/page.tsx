import type { Metadata } from "next";
import { FamilyCreate } from "@/features/families/family-create";
export const metadata: Metadata = { title: "Create family group" };
export default function NewFamilyPage() { return <FamilyCreate />; }
