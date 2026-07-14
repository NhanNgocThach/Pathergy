import { LoaderCircle } from "lucide-react";

export function Spinner({ label = "Loading" }: { label?: string }) {
  return <span className="inline-flex items-center gap-2" role="status"><LoaderCircle className="size-5 animate-spin" aria-hidden="true" /><span>{label}</span></span>;
}
