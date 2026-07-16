import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    id: "/",
    name: "Pathergy",
    short_name: "Pathergy",
    description: "An educational medication allergy screening and family health-record prototype.",
    start_url: "/app",
    scope: "/",
    display: "standalone",
    background_color: "#f6f8fa",
    theme_color: "#0b5d59",
    icons: [
      {
        src: "/icon",
        sizes: "512x512",
        type: "image/png",
        purpose: "any",
      },
      {
        src: "/icon",
        sizes: "512x512",
        type: "image/png",
        purpose: "maskable",
      },
    ],
  };
}
