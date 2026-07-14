"use client";

import * as React from "react";

import { AuthContext } from "@/features/auth/auth-provider";

export function useAuth() {
  const context = React.useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}
