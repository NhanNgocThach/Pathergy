import type { Metadata } from "next";
import { MedicationResults } from "@/features/medications/medication-results";
export const metadata: Metadata = { title: "Medication check result" };
export default async function MedicationResultsPage({ searchParams }: { searchParams: Promise<{ id?: string }> }) { const { id } = await searchParams; return <MedicationResults historyId={Number(id)} />; }
