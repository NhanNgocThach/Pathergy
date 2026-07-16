import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";

import "@/app/globals.css";
import { Providers } from "@/app/providers";
import { SkipLink } from "@/components/skip-link";

export const metadata: Metadata = {
  title: { default: "Pathergy", template: "%s | Pathergy" },
  description: "An educational personal health and family sharing prototype.",
  applicationName: "Pathergy",
  manifest: "/manifest.webmanifest",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "Pathergy",
  },
  formatDetection: {
    telephone: false,
  },
  other: {
    "apple-mobile-web-app-capable": "yes",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
  themeColor: "#0b5d59",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return <html lang="en" suppressHydrationWarning><body><Providers><SkipLink />{children}</Providers></body></html>;
}
