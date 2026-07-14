import type { Metadata } from "next";
import { FamilyDetail } from "@/features/families/family-detail";
export const metadata: Metadata = { title: "Family group" };
export default async function FamilyPage({ params }: { params: Promise<{ familyId: string }> }) { const { familyId } = await params; return <FamilyDetail familyId={Number(familyId)} />; }
