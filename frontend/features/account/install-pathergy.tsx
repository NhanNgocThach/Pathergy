"use client";

import { Download, ShieldCheck, Smartphone } from "lucide-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useI18n } from "@/i18n/i18n-provider";

export function InstallPathergy() {
  const { t } = useI18n();

  return <Card>
    <CardHeader>
      <CardTitle className="flex items-center gap-2">
        <Smartphone className="size-5 text-primary" aria-hidden="true" />
        {t("install.title")}
      </CardTitle>
      <CardDescription>{t("install.description")}</CardDescription>
    </CardHeader>
    <CardContent className="space-y-5">
      <div className="pwa-browser-instructions grid gap-4 sm:grid-cols-2">
        <section className="rounded-md border p-4">
          <h3 className="flex items-center gap-2 font-semibold">
            <Download className="size-4 text-primary" aria-hidden="true" />
            {t("install.iosTitle")}
          </h3>
          <p className="mt-2 text-sm text-muted-foreground">{t("install.iosSteps")}</p>
        </section>
        <section className="rounded-md border p-4">
          <h3 className="flex items-center gap-2 font-semibold">
            <Download className="size-4 text-primary" aria-hidden="true" />
            {t("install.androidTitle")}
          </h3>
          <p className="mt-2 text-sm text-muted-foreground">{t("install.androidSteps")}</p>
        </section>
      </div>
      <Alert className="pwa-installed-message">
        <AlertTitle>{t("install.installedTitle")}</AlertTitle>
        <AlertDescription>{t("install.installedDescription")}</AlertDescription>
      </Alert>
      <div className="flex gap-3 rounded-md bg-muted p-4 text-sm">
        <ShieldCheck className="mt-0.5 size-5 shrink-0 text-primary" aria-hidden="true" />
        <p>{t("install.security")}</p>
      </div>
    </CardContent>
  </Card>;
}
