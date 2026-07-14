import type { Metadata } from "next";
import { AllergyCreate } from "@/features/allergies/allergy-form";
export const metadata: Metadata = { title: "Add allergy record" };
export default function AddAllergyPage() { return <AllergyCreate />; }
