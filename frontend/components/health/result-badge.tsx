import { CircleAlert, Info, TriangleAlert } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { MedicationCheckStatus } from "@/types/health";
const labels = { POTENTIAL_ALLERGY_MATCH: "Potential allergy match", NO_RECORDED_MATCH_FOUND: "No recorded match found", UNABLE_TO_VERIFY: "Unable to verify" };
export function ResultBadge({ result }: { result: MedicationCheckStatus }) { const Icon = result === "POTENTIAL_ALLERGY_MATCH" ? CircleAlert : result === "UNABLE_TO_VERIFY" ? TriangleAlert : Info; return <Badge variant={result === "POTENTIAL_ALLERGY_MATCH" ? "destructive" : "secondary"}><Icon className="mr-1 size-3.5" aria-hidden="true" />{labels[result]}</Badge>; }
