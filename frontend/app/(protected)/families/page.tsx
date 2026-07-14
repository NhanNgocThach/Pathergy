import type { Metadata } from "next";
import { FamilyList } from "@/features/families/family-list";
export const metadata: Metadata = { title: "Families" };
export default function FamiliesPage() { return <FamilyList />; }
