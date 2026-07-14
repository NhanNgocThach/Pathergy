import { z } from "zod";

const dateOfBirth = z.string().min(1, "Enter a date of birth.").refine((value) => !Number.isNaN(Date.parse(value)), "Enter a valid date.").refine((value) => new Date(`${value}T00:00:00`) <= new Date(), "Date of birth cannot be in the future.");
export const patientSchema = z.object({ first_name: z.string().trim().min(1, "Enter a first name.").max(50), last_name: z.string().trim().min(1, "Enter a last name.").max(50), date_of_birth: dateOfBirth });
export type PatientValues = z.infer<typeof patientSchema>;

export const allergySchema = z.object({ substance: z.string().trim().min(2, "Enter at least 2 characters.").max(100), rxcui: z.string().trim().max(20).refine((value) => !value || /^\d+$/.test(value), "RxCUI must contain numbers only."), reaction: z.string().trim().max(200).refine((value) => !value || value.length >= 2, "Enter at least 2 characters or leave this blank."), severity: z.enum(["mild", "moderate", "severe"]) });
export type AllergyValues = z.infer<typeof allergySchema>;
export const medicationSchema = z.object({ medication_name: z.string().trim().min(2, "Enter at least 2 characters.").max(100) });
export type MedicationValues = z.infer<typeof medicationSchema>;
