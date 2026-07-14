import { apiRequest, refreshSession } from "@/lib/api-client";
import { tokenStore } from "@/lib/token-store";
import type {
  ChangePasswordValues,
  ForgotPasswordValues,
  LoginValues,
  RegisterValues,
  ResetPasswordValues,
} from "@/schemas/auth";
import type {
  AuthSession,
  CurrentUser,
  DevelopmentLinkResponse,
  MessageResponse,
  RegisterResponse,
  TokenPair,
} from "@/types/auth";

export const authService = {
  async login(values: LoginValues): Promise<CurrentUser> {
    const tokens = await apiRequest<TokenPair>("/auth/login", {
      auth: false,
      method: "POST",
      json: {
        ...values,
        // FastAPI stores the full User-Agent header separately. Keep the
        // user-facing device name short enough for LoginRequest (max 100).
        device_name: typeof navigator === "undefined" ? null : "Web browser",
        device_type: "browser",
      },
    });
    tokenStore.setTokens(tokens);
    try {
      return await this.currentUser();
    } catch (error) {
      tokenStore.clear();
      throw error;
    }
  },

  register(values: RegisterValues): Promise<RegisterResponse> {
    return apiRequest("/auth/register", {
      auth: false,
      method: "POST",
      json: {
        email: values.email,
        display_name: values.display_name,
        password: values.password,
        confirm_password: values.confirm_password,
        profile: {
          first_name: values.first_name,
          last_name: values.last_name,
          date_of_birth: values.date_of_birth,
        },
      },
    });
  },

  verifyEmail(token: string): Promise<MessageResponse> {
    return apiRequest("/auth/verify-email", {
      auth: false,
      method: "POST",
      json: { token },
    });
  },

  forgotPassword(values: ForgotPasswordValues): Promise<DevelopmentLinkResponse> {
    return apiRequest("/auth/forgot-password", {
      auth: false,
      method: "POST",
      json: values,
    });
  },

  resetPassword(token: string, values: ResetPasswordValues): Promise<MessageResponse> {
    return apiRequest("/auth/reset-password", {
      auth: false,
      method: "POST",
      json: {
        token,
        new_password: values.password,
        confirm_password: values.confirm_password,
      },
    });
  },

  changePassword(values: ChangePasswordValues): Promise<MessageResponse> {
    return apiRequest("/auth/change-password", {
      method: "POST",
      json: {
        current_password: values.current_password,
        new_password: values.password,
        confirm_password: values.confirm_password,
      },
    });
  },

  currentUser(): Promise<CurrentUser> {
    return apiRequest("/auth/me");
  },

  async restoreSession(): Promise<CurrentUser | null> {
    if (!tokenStore.getAccessToken()) {
      const refreshed = await refreshSession();
      if (!refreshed) return null;
    }
    try {
      return await this.currentUser();
    } catch {
      tokenStore.clear();
      return null;
    }
  },

  async logout(): Promise<void> {
    try {
      await apiRequest<void>("/auth/logout", { method: "POST" });
    } finally {
      tokenStore.clear();
    }
  },

  listSessions(): Promise<AuthSession[]> {
    return apiRequest("/auth/sessions");
  },

  revokeSession(sessionId: string): Promise<void> {
    return apiRequest(`/auth/sessions/${sessionId}`, { method: "DELETE" });
  },

  revokeAllSessions(): Promise<void> {
    return apiRequest("/auth/sessions", { method: "DELETE" });
  },
};
