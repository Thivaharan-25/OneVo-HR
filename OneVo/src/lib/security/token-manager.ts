let _accessToken: string | null = null;
let _expiresAt: number | null = null;

export const tokenManager = {
  set(token: string, expirySeconds: number): void {
    _accessToken = token;
    _expiresAt = Date.now() + expirySeconds * 1000;
  },
  get(): string | null {
    return _accessToken;
  },
  isExpiringSoon(): boolean {
    return _expiresAt !== null && Date.now() > _expiresAt - 60_000;
  },
  clear(): void {
    _accessToken = null;
    _expiresAt = null;
  },
};
