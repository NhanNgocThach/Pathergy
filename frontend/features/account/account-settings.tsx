"use client";

import { KeyRound, LogOut, MonitorSmartphone } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { PageHeader } from "@/components/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { InstallPathergy } from "@/features/account/install-pathergy";
import { useAuth } from "@/hooks/use-auth";
import { useI18n } from "@/i18n/i18n-provider";
import { formatDateTime } from "@/lib/format";

export function AccountSettings() {
  const { user, logout } = useAuth();
  const { t } = useI18n();
  const router = useRouter();

  async function signOut() {
    await logout();
    router.replace("/login");
  }

  const verificationDate = user?.email_verified_at ?? user?.phone_verified_at;

  return (
    <>
      <PageHeader title={t("settings.title")} description={t("settings.description")} />
      <Card>
        <CardHeader>
          <CardTitle>{t("settings.summary")}</CardTitle>
        </CardHeader>
        <CardContent>
          <dl className="grid gap-4 sm:grid-cols-2">
            <div>
              <dt className="text-sm text-muted-foreground">{t("register.displayName")}</dt>
              <dd className="font-semibold">{user?.display_name}</dd>
            </div>
            {user?.email ? (
              <div>
                <dt className="text-sm text-muted-foreground">{t("auth.email")}</dt>
                <dd className="break-all font-semibold">{user.email}</dd>
              </div>
            ) : null}
            {user?.phone_number_masked ? (
              <div>
                <dt className="text-sm text-muted-foreground">{t("settings.phone")}</dt>
                <dd className="font-semibold">{user.phone_number_masked}</dd>
              </div>
            ) : null}
            <div>
              <dt className="text-sm text-muted-foreground">{t("settings.verificationStatus")}</dt>
              <dd>
                <Badge>{verificationDate ? t("settings.verified") : t("settings.notVerified")}</Badge>
                {verificationDate ? (
                  <span className="ml-2 text-sm">{formatDateTime(verificationDate)}</span>
                ) : null}
              </dd>
            </div>
            <div>
              <dt className="text-sm text-muted-foreground">{t("settings.userId")}</dt>
              <dd className="font-semibold">{user?.user_id}</dd>
            </div>
          </dl>
          <p className="mt-5 rounded-md bg-muted p-4 text-sm">{t("settings.readOnly")}</p>
        </CardContent>
      </Card>
      <InstallPathergy />
      <Card>
        <CardHeader>
          <CardTitle>{t("settings.security")}</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-3">
          <Button asChild variant="outline">
            <Link href="/change-password">
              <KeyRound className="size-4" />
              {t("auth.changePassword")}
            </Link>
          </Button>
          <Button asChild variant="outline">
            <Link href="/security/sessions">
              <MonitorSmartphone className="size-4" />
              {t("auth.activeSessions")}
            </Link>
          </Button>
          <Button variant="destructive" onClick={() => void signOut()}>
            <LogOut className="size-4" />
            {t("auth.logout")}
          </Button>
        </CardContent>
      </Card>
    </>
  );
}
