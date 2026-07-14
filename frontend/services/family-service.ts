import { apiRequest } from "@/lib/api-client";
import type { FamilyGroupValues, MembershipUpdateValues, MembershipValues } from "@/schemas/family";
import type { EnforcedPermissionType, FamilyGroup, FamilyMembership, FamilyPermission, UserFamilyGroup } from "@/types/family";

export const familyService = {
  listForUser: (userId: number) => apiRequest<UserFamilyGroup[]>(`/users/${userId}/family-groups`),
  get: (groupId: number) => apiRequest<FamilyGroup>(`/family-groups/${groupId}`),
  create: (values: FamilyGroupValues) => apiRequest<FamilyGroup>("/family-groups", { method: "POST", json: values }),
  update: (groupId: number, values: FamilyGroupValues) => apiRequest<FamilyGroup>(`/family-groups/${groupId}`, { method: "PUT", json: values }),
  members: (groupId: number) => apiRequest<FamilyMembership[]>(`/family-groups/${groupId}/members`),
  addMember: (groupId: number, values: MembershipValues) => apiRequest<FamilyMembership>(`/family-groups/${groupId}/members`, { method: "POST", json: values }),
  updateMember: (groupId: number, userId: number, values: Partial<MembershipUpdateValues>) => apiRequest<FamilyMembership>(`/family-groups/${groupId}/members/${userId}`, { method: "PUT", json: values }),
  removeMember: (groupId: number, userId: number) => apiRequest<FamilyMembership>(`/family-groups/${groupId}/members/${userId}`, { method: "DELETE" }),
  leave: (groupId: number, userId: number) => apiRequest<FamilyMembership>(`/family-groups/${groupId}/members/${userId}/leave`, { method: "POST" }),
  permissions: (groupId: number, userId: number) => apiRequest<FamilyPermission[]>(`/family-groups/${groupId}/members/${userId}/permissions`),
  updatePermissions: (groupId: number, userId: number, permissions: Array<{ data_type: EnforcedPermissionType; can_view: boolean; can_edit: boolean }>) => apiRequest<FamilyPermission[]>(`/family-groups/${groupId}/members/${userId}/permissions`, { method: "PUT", json: { permissions } }),
};
