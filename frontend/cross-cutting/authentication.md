# Authentication (Frontend)

## Browser Session Model

The customer-facing ONEVO web app uses a BFF-style cookie session model.

Browser JavaScript never receives, stores, decodes, or sends the tenant user JWT. The backend owns token creation, refresh, validation, rotation, and revocation. The frontend only receives user/session state and permission metadata.

## Auth Flow

```text
User                 Frontend App                  Backend API
 |                       |                              |
 |-- credentials ------->|                              |
 |                       |-- POST /api/v1/auth/login -->|
 |                       |   credentials: include       |
 |                       |                              |-- verify password
 |                       |                              |-- require TOTP if needed
 |                       |<-- 200/202 ------------------|
 |                       |   Set-Cookie: onevo_session  |
 |                       |   Body: user, permissions,   |
 |                       |         mfa_required flags   |
 |<-- dashboard ---------|                              |
```

If MFA is required, `/api/v1/auth/login` returns `mfa_required: true` without creating a full application session. After the user verifies the authenticator-app TOTP code, `/api/v1/auth/mfa/verify` creates or upgrades the HttpOnly session cookie and returns the same safe session metadata.

## Cookie And Session Handling

| Item | Storage | Lifetime | Sent As |
|:-----|:--------|:---------|:--------|
| Web session | HttpOnly Secure SameSite cookie | Server controlled | Automatic via `credentials: "include"` |
| CSRF token | Readable CSRF cookie plus `X-CSRF-Token` header | Server controlled | Header on mutations |
| User/permissions | Zustand memory state | Current page lifecycle | Not an auth credential |

No access token manager exists for the browser app. Do not add `token-manager.ts` for customer web auth.

## Initial Session Check

On app load, the frontend calls `/api/v1/auth/session` or `/api/v1/auth/refresh` with `credentials: "include"`.

```tsx
export async function initializeAuth(): Promise<boolean> {
  const response = await fetch(`${API_URL}/api/v1/auth/session`, {
    method: 'GET',
    credentials: 'include',
  });

  if (!response.ok) return false;

  const data = await response.json();
  useAuthStore.getState().setSession(data.user, data.permissions, data.active_modules);
  return true;
}
```

The browser does not parse JWT claims. Permissions, tenant identity, module entitlements, and display user data come from backend session endpoints.

## Session Refresh

Session refresh is cookie based:

```tsx
export async function refreshSession(): Promise<boolean> {
  const response = await fetch(`${API_URL}/api/v1/auth/refresh`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'X-CSRF-Token': getCsrfToken(),
    },
  });

  if (!response.ok) return false;

  const data = await response.json();
  useAuthStore.getState().setSession(data.user, data.permissions, data.active_modules);
  return true;
}
```

The backend may rotate internal JWTs, refresh records, or session records during this call. None of those tokens are exposed to browser JavaScript.

## Auth Provider

```tsx
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    initializeAuth()
      .then((success) => {
        if (!success && !isPublicRoute(window.location.pathname)) {
          window.location.href = `/login?redirect=${window.location.pathname}`;
        }
      })
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) return <FullPageSpinner />;

  return <>{children}</>;
}
```

## Auth Store

```tsx
interface AuthState {
  user: User | null;
  permissions: string[];
  activeModules: string[];
  tenantId: string | null;
  isAuthenticated: boolean;
  setSession: (user: User, permissions: string[], activeModules: string[]) => void;
  clear: () => void;
  hasPermission: (permission: string) => boolean;
  hasAnyPermission: (...permissions: string[]) => boolean;
  hasAllPermissions: (...permissions: string[]) => boolean;
}
```

The store contains authorization metadata, not credentials.

## Logout

```tsx
async function logout() {
  await api.auth.logout();

  useAuthStore.getState().clear();
  queryClient.clear();
  signalRConnection?.stop();

  window.location.href = '/login';
}
```

`/api/v1/auth/logout` revokes the server-side session and clears the HttpOnly session cookie.

## Multi-Tab Session Sync

Use `BroadcastChannel` only to sync state changes such as logout or session refresh completion. Never broadcast JWTs or session cookie values.

```tsx
const authChannel = new BroadcastChannel('auth');

authChannel.onmessage = (event) => {
  if (event.data.type === 'LOGOUT') {
    useAuthStore.getState().clear();
    window.location.href = '/login';
  }
  if (event.data.type === 'SESSION_REFRESHED') {
    initializeAuth();
  }
};
```

## Non-Browser Clients

This page describes the customer web frontend only. IDE extensions, desktop agents, platform-admin internals, and service integrations may still use JWT Bearer tokens through their own documented storage and authentication rules.

## Related

- [[frontend/cross-cutting/authorization|Authorization]] - RBAC permission system
- [[frontend/cross-cutting/security|Security]] - XSS, CSRF protection
- [[frontend/data-layer/api-integration|Api Integration]] - API client auth behavior
- [[frontend/architecture/routing|Routing]] - route guards
