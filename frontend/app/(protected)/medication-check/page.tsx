import type { Metadata } from "next";
import { MedicationCheck } from "@/features/medications/medication-check";
export const metadata: Metadata = { title: "Medication Check" };
export default function MedicationCheckPage() { return <MedicationCheck />; }
