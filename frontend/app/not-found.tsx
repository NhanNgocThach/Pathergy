import Link from "next/link";

import { Button } from "@/components/ui/button";

export default function NotFound() {
  return <main className="mx-auto flex min-h-screen max-w-lg flex-col items-center justify-center gap-4 px-4 text-center"><p className="text-sm font-semibold text-primary">404</p><h1 className="text-3xl font-bold">Page not found</h1><p className="text-muted-foreground">The requested page is not available.</p><Button asChild><Link href="/">Return to Pathergy</Link></Button></main>;
}
