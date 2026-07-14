"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import * as React from "react";

import { useAuth } from "@/hooks/use-auth";
import { apiRequest } from "@/lib/api-client";
import { queryKeys } from "@/lib/query-keys";
import { familyService } from "@/services/family-service";
import { patientService } from "@/services/health-service";
import type { FamilyRelationship } from "@/types/family";
import type { Patient } from "@/types/health";

export type ProfileOption = Patient & { isOwn: boolean; familyGroupId?: number; familyGroupName?: string; relationship?: FamilyRelationship };
export type ProfileContextValue = { profiles: ProfileOption[]; selected: ProfileOption | null; selectedPatientId: number | null; selectPatient: (patientId: number) => void; isLoading: boolean; error: Error | null };
export const ProfileContext = React.createContext<ProfileContextValue | null>(null);

async function discoverProfiles(userId: number, ownPatientId: number): Promise<ProfileOption[]> {
  const [patients, groups] = await Promise.all([patientService.list(), familyService.listForUser(userId)]);
  const contexts = new Map<number, Omit<ProfileOption, keyof Patient>>();
  contexts.set(ownPatientId, { isOwn: true });
  const activeGroups = groups.filter((entry) => entry.membership.status === "ACTIVE");
  await Promise.all(activeGroups.map(async ({ family_group: group }) => {
    try {
      const members = await familyService.members(group.family_group_id);
      await Promise.all(members.filter((member) => member.status === "ACTIVE" && member.user_id !== userId).map(async (member) => {
        try {
        const profile = await apiRequest<Patient>(`/users/${member.user_id}/profile`);
        if (!contexts.has(profile.id)) contexts.set(profile.id, { isOwn: false, familyGroupId: group.family_group_id, familyGroupName: group.name, relationship: member.relationship });
        } catch { /* A non-shared basic profile is intentionally not discoverable. */ }
      }));
    } catch { /* One inaccessible family must not hide otherwise available profiles. */ }
  }));
  return patients.map((patient) => ({ ...patient, ...(contexts.get(patient.id) ?? { isOwn: patient.id === ownPatientId }) })).sort((a, b) => Number(b.isOwn) - Number(a.isOwn) || a.first_name.localeCompare(b.first_name));
}

export function ProfileProvider({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [selectedPatientId, setSelectedPatientId] = React.useState<number | null>(user?.patient_id ?? null);
  const profilesQuery = useQuery({ queryKey: queryKeys.patients, queryFn: () => discoverProfiles(user!.user_id, user!.patient_id), enabled: Boolean(user), staleTime: 30_000, gcTime: 60_000 });
  const selectPatient = React.useCallback((patientId: number) => {
    if (selectedPatientId && selectedPatientId !== patientId) queryClient.removeQueries({ queryKey: ["patient-data", selectedPatientId] });
    setSelectedPatientId(patientId);
  }, [queryClient, selectedPatientId]);
  const profiles = profilesQuery.data ?? [];
  const selected = profiles.find((profile) => profile.id === selectedPatientId) ?? profiles.find((profile) => profile.isOwn) ?? null;
  return <ProfileContext.Provider value={{ profiles, selected, selectedPatientId: selected?.id ?? selectedPatientId, selectPatient, isLoading: profilesQuery.isLoading, error: profilesQuery.error }}>{children}</ProfileContext.Provider>;
}
