import type { Metadata } from "next";
import { AllergyEdit } from "@/features/allergies/allergy-form";
export const metadata: Metadata = { title: "Edit allergy record" };
export default async function EditAllergyPage({ params }: { params: Promise<{ allergyId: string }> }) { const { allergyId } = await params; return <AllergyEdit allergyId={Number(allergyId)} />; }
