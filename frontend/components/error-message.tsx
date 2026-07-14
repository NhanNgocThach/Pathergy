import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

export function ErrorMessage({ message, title = "Unable to continue" }: { message: string; title?: string }) {
  return <Alert variant="destructive"><AlertTitle>{title}</AlertTitle><AlertDescription>{message}</AlertDescription></Alert>;
}
