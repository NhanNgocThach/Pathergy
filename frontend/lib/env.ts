import { ApiError } from "@/types/api";

export function getApiBaseUrl(): string {
  const value = process.env.NEXT_PUBLIC_API_BASE_URL?.trim().replace(/\/$/, "");
  if (!value) {
    throw new ApiError(
      0,
      "CONFIGURATION_ERROR",
      "The frontend API base URL is not configured.",
    );
  }
  return value;
}
