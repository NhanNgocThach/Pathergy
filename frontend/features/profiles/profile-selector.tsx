"use client";

import { FormField } from "@/components/form-field";
import { Select } from "@/components/ui/select";
import { Spinner } from "@/components/spinner";
import { useProfile } from "@/hooks/use-profile";
import { useI18n } from "@/i18n/i18n-provider";
import { formatPersonName } from "@/lib/format";

export function ProfileSelector({ label }: { label?: string }) {
  const { locale, t } = useI18n();
  const { profiles, selectedPatientId, selectPatient, isLoading } = useProfile();
  const visibleLabel = label ?? t("profile.viewing");
  if (isLoading) return <Spinner label={t("profile.loadingAvailable")} />;
  if (profiles.length <= 1) return profiles[0] ? <div className="rounded-md border bg-card px-4 py-3"><p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{visibleLabel}</p><p className="font-semibold">{t("profile.mine")} — {formatPersonName(profiles[0].first_name, profiles[0].last_name, locale)}</p></div> : null;
  return <div className="max-w-md"><FormField id="profile-selector" label={visibleLabel} hint={t("profile.switchHint")}><Select id="profile-selector" value={selectedPatientId ?? ""} onChange={(event) => selectPatient(Number(event.target.value))}>{profiles.map((profile) => <option key={profile.id} value={profile.id}>{profile.isOwn ? t("profile.mine") : t("profile.shared")} — {formatPersonName(profile.first_name, profile.last_name, locale)}{profile.familyGroupName ? ` · ${profile.familyGroupName} · ${profile.relationship}` : ""}</option>)}</Select></FormField></div>;
}
