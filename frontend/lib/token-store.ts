import type { TokenPair } from "@/types/auth";

const REFRESH_TOKEN_KEY = "pathergy.refresh-token";
type TokenListener = () => void;

class TokenStore {
  private accessToken: string | null = null;
  private listeners = new Set<TokenListener>();

  getAccessToken(): string | null {
    return this.accessToken;
  }

  getRefreshToken(): string | null {
    if (typeof window === "undefined") return null;
    return window.sessionStorage.getItem(REFRESH_TOKEN_KEY);
  }

  setTokens(tokens: TokenPair): void {
    this.accessToken = tokens.access_token;
    if (typeof window !== "undefined") {
      window.sessionStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
    }
    this.emit();
  }

  clear(): void {
    this.accessToken = null;
    if (typeof window !== "undefined") {
      window.sessionStorage.removeItem(REFRESH_TOKEN_KEY);
    }
    this.emit();
  }

  subscribe(listener: TokenListener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private emit(): void {
    this.listeners.forEach((listener) => listener());
  }
}

export const tokenStore = new TokenStore();
