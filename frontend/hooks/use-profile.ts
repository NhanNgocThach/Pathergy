"use client";
import * as React from "react";
import { ProfileContext } from "@/features/profiles/profile-provider";
export function useProfile() { const value = React.useContext(ProfileContext); if (!value) throw new Error("useProfile must be used inside ProfileProvider"); return value; }
