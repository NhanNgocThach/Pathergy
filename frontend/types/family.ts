export type FamilyRole = "OWNER" | "ADMIN" | "MEMBER";
export type FamilyRelationship = "SELF" | "SPOUSE" | "CHILD" | "PARENT" | "SIBLING" | "RELATIVE" | "CAREGIVER" | "OTHER";
export type MembershipStatus = "PENDING" | "ACTIVE" | "LEFT" | "REMOVED" | "DECLINED";
export type EnforcedPermissionType = "BASIC_PROFILE" | "ALLERGIES" | "SCREENING_HISTORY";
export type FamilyGroup = { family_group_id: number; name: string; created_by_user_id: number; created_at: string; updated_at: string; is_active: boolean };
export type FamilyMembership = { membership_id: number; family_group_id: number; user_id: number; role: FamilyRole; relationship: FamilyRelationship; status: MembershipStatus; joined_at: string | null; left_at: string | null; created_at: string; updated_at: string };
export type UserFamilyGroup = { family_group: FamilyGroup; membership: FamilyMembership };
export type FamilyPermission = { permission_id: number; membership_id: number; data_type: "BASIC_PROFILE" | "ALLERGIES" | "CURRENT_MEDICATIONS" | "SCREENING_HISTORY" | "MEDICAL_DOCUMENTS" | "EMERGENCY_INFORMATION"; can_view: boolean; can_edit: boolean; created_at: string; updated_at: string };
