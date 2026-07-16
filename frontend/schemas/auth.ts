import { z } from "zod";

const password = z
  .string()
  .min(6, "Password must be at least 6 characters.")
  .max(128, "Password must be 128 characters or fewer.");

function isEmailOrVietnamesePhone(value: string) {
  if (z.email().safeParse(value).success) return true;
  const compact = value.replace(/[\s().-]+/g, "");
  return /^(?:0\d{9}|84\d{9}|\+84\d{9})$/.test(compact);
}

export const loginSchema = z.object({
  identifier: z
    .string()
    .trim()
    .min(1, "Enter your email address or phone number.")
    .refine(
      isEmailOrVietnamesePhone,
      "Enter a valid email address or Vietnamese phone number.",
    ),
  password: z.string().min(1, "Enter your password.").max(128),
});

export const registerSchema = z
  .object({
    display_name: z.string().trim().min(1, "Enter a display name.").max(100),
    email: z.email("Enter a valid email address."),
    password,
    confirm_password: z.string().min(1, "Confirm your password.").max(128),
    first_name: z.string().trim().min(1, "Enter your first name.").max(50),
    last_name: z.string().trim().min(1, "Enter your last name.").max(50),
    date_of_birth: z
      .string()
      .min(1, "Enter your date of birth.")
      .refine((value) => !Number.isNaN(Date.parse(value)), "Enter a valid date.")
      .refine(
        (value) => new Date(`${value}T00:00:00`) <= new Date(),
        "Date of birth cannot be in the future.",
      ),
    accept_notices: z.boolean().refine((value) => value, {
      message: "Accept the educational and privacy notices to continue.",
    }),
  })
  .refine((value) => value.password === value.confirm_password, {
    message: "The passwords do not match.",
    path: ["confirm_password"],
  });

export const forgotPasswordSchema = z.object({
  email: z.email("Enter a valid email address."),
});

export const resetPasswordSchema = z
  .object({
    password,
    confirm_password: z.string().min(1, "Confirm your password.").max(128),
  })
  .refine((value) => value.password === value.confirm_password, {
    message: "The passwords do not match.",
    path: ["confirm_password"],
  });

export const changePasswordSchema = z
  .object({
    current_password: z.string().min(1, "Enter your current password.").max(128),
    password,
    confirm_password: z.string().min(1, "Confirm your password.").max(128),
  })
  .refine((value) => value.password === value.confirm_password, {
    message: "The passwords do not match.",
    path: ["confirm_password"],
  });

export type LoginValues = z.infer<typeof loginSchema>;
export type RegisterValues = z.infer<typeof registerSchema>;
export type ForgotPasswordValues = z.infer<typeof forgotPasswordSchema>;
export type ResetPasswordValues = z.infer<typeof resetPasswordSchema>;
export type ChangePasswordValues = z.infer<typeof changePasswordSchema>;
