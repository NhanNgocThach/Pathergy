"use client";

import { FormField } from "@/components/form-field";
import { Select } from "@/components/ui/select";
import { Spinner } from "@/components/spinner";
import { useProfile } from "@/hooks/use-profile";

export function ProfileSelector({ label = "Viewing profile" }: { label?: string }) {
  const { profiles, selectedPatientId, selectPatient, isLoading } = useProfile();
  if (isLoading) return <Spinner label="Loading available profiles" />;
  if (profiles.length <= 1) return profiles[0] ? <div className="rounded-md border bg-card px-4 py-3"><p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">{label}</p><p className="font-semibold">My profile — {profiles[0].first_name} {profiles[0].last_name}</p></div> : null;
  return <div className="max-w-md"><FormField id="profile-selector" label={label} hint="Health information is kept separate when you switch profiles."><Select id="profile-selector" value={selectedPatientId ?? ""} onChange={(event) => selectPatient(Number(event.target.value))}>{profiles.map((profile) => <option key={profile.id} value={profile.id}>{profile.isOwn ? "My profile" : "Shared profile"} — {profile.first_name} {profile.last_name}{profile.familyGroupName ? ` · ${profile.familyGroupName} · ${profile.relationship}` : ""}</option>)}</Select></FormField></div>;
}
