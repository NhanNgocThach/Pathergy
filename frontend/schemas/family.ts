import { z } from "zod";
export const familyGroupSchema = z.object({ name: z.string().trim().min(1, "Enter a family name.").max(100) });
export type FamilyGroupValues = z.infer<typeof familyGroupSchema>;
export const membershipSchema = z.object({ user_id: z.number().int().positive("Enter a valid user ID."), role: z.enum(["OWNER", "ADMIN", "MEMBER"]), relationship: z.enum(["SELF", "SPOUSE", "CHILD", "PARENT", "SIBLING", "RELATIVE", "CAREGIVER", "OTHER"]) });
export type MembershipValues = z.infer<typeof membershipSchema>;
export const membershipUpdateSchema = z.object({ role: z.enum(["OWNER", "ADMIN", "MEMBER"]), relationship: z.enum(["SELF", "SPOUSE", "CHILD", "PARENT", "SIBLING", "RELATIVE", "CAREGIVER", "OTHER"]), status: z.enum(["PENDING", "ACTIVE", "DECLINED"]) });
export type MembershipUpdateValues = z.infer<typeof membershipUpdateSchema>;
