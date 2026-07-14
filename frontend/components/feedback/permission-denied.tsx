import { LockKeyhole } from "lucide-react";
import { EmptyState } from "@/components/empty-state";
export function PermissionDenied({ description = "This profile has not shared access to this information." }: { description?: string }) { return <EmptyState icon={LockKeyhole} title="Permission required" description={description} />; }
