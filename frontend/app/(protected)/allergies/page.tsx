import type { Metadata } from "next";
import { AllergyList } from "@/features/allergies/allergy-list";
export const metadata: Metadata = { title: "Allergies" };
export default function AllergiesPage() { return <AllergyList />; }
