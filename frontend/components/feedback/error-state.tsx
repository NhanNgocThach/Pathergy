import { Button } from "@/components/ui/button";
import { StatusPanel } from "@/components/feedback/status-panel";
export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) { return <StatusPanel tone="error" title="The request could not be completed" actions={onRetry ? <Button variant="outline" onClick={onRetry}>Try again</Button> : undefined}><p>{message}</p></StatusPanel>; }
