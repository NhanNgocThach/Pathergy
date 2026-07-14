import type { Metadata } from "next";
import type { ReactNode } from "react";

import "@/app/globals.css";
import { Providers } from "@/app/providers";

export const metadata: Metadata = {
  title: { default: "Pathergy", template: "%s | Pathergy" },
  description: "An educational personal health and family sharing prototype.",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return <html lang="en"><body><a href="#main-content" className="skip-link">Skip to main content</a><Providers>{children}</Providers></body></html>;
}
