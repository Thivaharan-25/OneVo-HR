# Frontend Authentication Flow

## Customer Web Login Flow

```text
User                    Frontend App              Backend API
  |                        |                          |
  |-- Enter credentials -->|                          |
  |                        |-- POST /auth/login ----->|
  |                        |   credentials: include   |-- Verify password
  |                        |                          |-- Run MFA policy
  |                        |<-- 200/202 --------------|
  |                        |   Set-Cookie:            |
  |                        |   onevo_session          |
  |                        |   Body: session metadata |
  |<-- Redirect to --------|                          |
  |   /overview            |                          |
```

The customer browser frontend never receives the tenant user JWT. This is a BFF-style session model: backend token/session logic stays on the server, and the browser sends only HttpOnly cookies automatically.

## Session Storage

| Item | Where | Why |
|:-----|:------|:----|
| Web session cookie | HttpOnly Secure SameSite cookie | Not accessible to JavaScript |
| CSRF token | Readable CSRF cookie plus `X-CSRF-Token` header | Protects cookie-authenticated mutations |
| User and permissions | Frontend memory state | UI metadata only, not an auth credential |

Never store tenant JWTs in `localStorage`, `sessionStorage`, browser-readable cookies, or frontend memory for customer web auth.

## Session Refresh

```text
1. Frontend calls POST /auth/refresh with credentials: include
2. Browser sends HttpOnly session cookie automatically
3. Backend validates and rotates server-side session/token state
4. Backend returns safe session metadata: user, permissions, active modules
5. Backend sets or rotates the HttpOnly session cookie
6. If refresh fails, frontend clears UI state and redirects to /login
```

### Concurrent Request Handling

When multiple requests detect an expired session simultaneously:

- First failure triggers refresh.
- Other failures queue and wait for refresh to complete.
- If refresh succeeds, requests retry with the same cookie-based session.
- If refresh fails, all pending requests fail with `AuthError` and the user returns to login.

```typescript
let refreshPromise: Promise<SessionDto | null> | null = null;

async function refreshSessionOnce(): Promise<SessionDto | null> {
  if (!refreshPromise) {
    refreshPromise = api.post('/auth/refresh').finally(() => {
      refreshPromise = null;
    });
  }
  return refreshPromise;
}
```

## MFA Flow

```text
User                    Frontend                  Backend
  |-- Login ------------>|-- POST /auth/login ---->|
  |                      |<-- 202: { mfa_required }|
  |<-- Show MFA page ----|                          |
  |-- Enter TOTP code -->|-- POST /auth/mfa/verify>|
  |                      |<-- 200 + Set-Cookie ----|
  |<-- Redirect ---------|                          |
```

Primary MFA uses authenticator-app TOTP. Email OTP is fallback/recovery only when tenant policy allows it.

## AuthProvider

```tsx
interface AuthContext {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  permissions: string[];
  activeModules: string[];
  hasPermission: (p: string) => boolean;
  hasAnyPermission: (...p: string[]) => boolean;
  login: (credentials: LoginInput) => Promise<void>;
  logout: () => Promise<void>;
  refreshSession: () => Promise<void>;
}
```

### Initial Load

On app start:

1. Try `GET /auth/session` or `POST /auth/refresh` with `credentials: "include"`.
2. If success, store user, permissions, and active modules in memory.
3. If failure, user is not logged in; protected routes redirect to `/login`.

## Route Protection

```tsx
export default function DashboardLayout({ children }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) return <FullPageSpinner />;
  if (!isAuthenticated) redirect('/login');

  return <DashboardShell>{children}</DashboardShell>;
}
```

## Logout

```text
1. POST /auth/logout with credentials: include
2. Backend revokes session and clears HttpOnly cookie
3. Frontend clears AuthService signals and destroys active resources
4. Frontend redirects to /login
```

## Non-Browser Clients

This flow is only for the customer web frontend. IDE extension auth, desktop agent device auth, platform-admin server internals, and service integrations may still use JWT Bearer tokens where their own contracts require them.

## Related

- [[frontend/cross-cutting/authentication|Authentication]]
- [[security/auth-architecture|Auth Architecture]]
- [[modules/auth/session-management/overview|Session Management]]
- [[modules/auth/mfa/overview|MFA]]
- [[frontend/data-layer/api-integration|API Integration]]
