import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, type RenderOptions } from "@testing-library/react";
import type { ReactElement, ReactNode } from "react";

import { AuthProvider } from "@/features/auth/auth-provider";
import { ToastProvider } from "@/components/feedback/toast-provider";
import { ProfileContext, type ProfileContextValue, type ProfileOption } from "@/features/profiles/profile-provider";

function TestProviders({ children }: { children: ReactNode }) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } });
  return <QueryClientProvider client={queryClient}><AuthProvider><ToastProvider>{children}</ToastProvider></AuthProvider></QueryClientProvider>;
}

export function renderWithProviders(ui: ReactElement, options?: Omit<RenderOptions, "wrapper">) {
  return render(ui, { wrapper: TestProviders, ...options });
}

export const fictionalProfile: ProfileOption = { id: 10, first_name: "Fictional", last_name: "User", date_of_birth: "1990-01-01", isOwn: true };

export function renderWithProfile(ui: ReactElement, overrides: Partial<ProfileContextValue> = {}) {
  const value: ProfileContextValue = { profiles: [fictionalProfile], selected: fictionalProfile, selectedPatientId: 10, selectPatient: () => undefined, isLoading: false, error: null, ...overrides };
  return renderWithProviders(<ProfileContext.Provider value={value}>{ui}</ProfileContext.Provider>);
}

export * from "@testing-library/react";
export { default as userEvent } from "@testing-library/user-event";
