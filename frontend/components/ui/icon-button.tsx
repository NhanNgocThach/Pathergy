import type { ComponentProps } from "react";
import { Button } from "@/components/ui/button";
export function IconButton({ "aria-label": label, ...props }: ComponentProps<typeof Button>) { if (!label) throw new Error("IconButton requires an accessible label"); return <Button size="icon" aria-label={label} {...props} />; }
