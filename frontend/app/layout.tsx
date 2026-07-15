import type { Metadata } from "next";
import type { ReactNode } from "react";

import "@/app/globals.css";
import { Providers } from "@/app/providers";
import { SkipLink } from "@/components/skip-link";

export const metadata: Metadata = {
  title: { default: "Pathergy", template: "%s | Pathergy" },
  description: "An educational personal health and family sharing prototype.",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return <html lang="en" suppressHydrationWarning><body><Providers><SkipLink />{children}</Providers></body></html>;
}
