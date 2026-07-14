"use client";

import * as React from "react";
import { useQueryClient } from "@tanstack/react-query";

import { tokenStore } from "@/lib/token-store";
import type { LoginValues, RegisterValues } from "@/schemas/auth";
import { authService } from "@/services/auth-service";
import type { CurrentUser, RegisterResponse } from "@/types/auth";

type AuthContextValue = {
  user: CurrentUser | null;
  isLoading: boolean;
  login: (values: LoginValues) => Promise<CurrentUser>;
  register: (values: RegisterValues) => Promise<RegisterResponse>;
  logout: () => Promise<void>;
  refreshSession: () => Promise<CurrentUser | null>;
};

export const AuthContext = React.createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const queryClient = useQueryClient();
  const [user, setUser] = React.useState<CurrentUser | null>(null);
  const [isLoading, setIsLoading] = React.useState(true);

  const restore = React.useCallback(async () => {
    setIsLoading(true);
    const restored = await authService.restoreSession();
    setUser(restored);
    setIsLoading(false);
    return restored;
  }, []);

  React.useEffect(() => {
    let active = true;
    void authService.restoreSession().then((restored) => {
      if (active) {
        setUser(restored);
        setIsLoading(false);
      }
    });
    const unsubscribe = tokenStore.subscribe(() => {
      if (!tokenStore.getAccessToken() && !tokenStore.getRefreshToken()) {
        queryClient.clear();
        setUser(null);
      }
    });
    return () => {
      active = false;
      unsubscribe();
    };
  }, [queryClient]);

  const value = React.useMemo<AuthContextValue>(
    () => ({
      user,
      isLoading,
      async login(values) {
        const authenticatedUser = await authService.login(values);
        setUser(authenticatedUser);
        return authenticatedUser;
      },
      register: (values) => authService.register(values),
      async logout() {
        await authService.logout();
        queryClient.clear();
        setUser(null);
      },
      refreshSession: restore,
    }),
    [user, isLoading, restore, queryClient],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
