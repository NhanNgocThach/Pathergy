export type CurrentUser = {
  user_id: number;
  email: string | null;
  phone_number_masked: string | null;
  display_name: string;
  patient_id: number;
  email_verified_at: string | null;
  phone_verified_at: string | null;
  is_active: boolean;
};

export type TokenPair = {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
  access_token_expires_in: number;
  refresh_token_expires_in: number;
};

export type RegisterResponse = {
  user_id: number;
  email: string;
  patient_id: number;
  verification_required: boolean;
  verification_url: string | null;
};

export type MessageResponse = {
  message: string;
};

export type DevelopmentLinkResponse = MessageResponse & {
  development_url: string | null;
};

export type AuthSession = {
  session_id: string;
  device_name: string | null;
  device_type: string | null;
  ip_address: string | null;
  user_agent: string | null;
  created_at: string;
  last_used_at: string;
  expires_at: string;
  is_current: boolean;
};
