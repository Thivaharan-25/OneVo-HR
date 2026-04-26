# Frontend Authentication Flow

## Login Flow

```
User                    Frontend App              Backend API
  |                        |                          |
  |-- Enter credentials -->|                          |
  |                        |-- POST /auth/login ------>|
  |                        |                          |-- Verify (Argon2id)
  |                        |<-- 200: { accessToken } --|
  |                        |   + Set-Cookie: refresh   |
  |                        |                          |
  |                        |-- Store accessToken       |
  |                        |   in memory (NOT storage) |
  |                        |                          |
  |<-- Redirect to --------|                          |
  |   /overview            |                          |
```

## Token Storage

| Token | Where | Why |
|:------|:------|:----|
| Access token (JWT) | In-memory variable (AuthProvider state) | Short-lived (15 min), XSS can't exfiltrate from JS memory |
| Refresh token | HttpOnly Secure SameSite=Strict cookie | Not accessible to JS at all |

**NEVER** store the access token in localStorage, sessionStorage, or cookies accessible to JS.

## Token Refresh

```
1. API call returns 401 (access token expired)
2. ApiClient interceptor catches 401
3. POST /auth/refresh (refresh token cookie sent automatically)
4. Backend validates refresh token, rotates it
5. New access token returned in body, new refresh cookie set
6. Retry original request with new access token
7. If refresh fails (403) → redirect to /login
```

### Concurrent Request Handling

When multiple requests fail with 401 simultaneously:
- First failure triggers the refresh
- Other failures queue and wait for refresh to complete
- All retry with the new access token
- Implemented via a shared promise in the ApiClient

```typescript
// Pattern in api-client.ts
let refreshPromise: Promise<string> | null = null;

async function refreshAccessToken(): Promise<string> {
  if (!refreshPromise) {
    refreshPromise = api.post('/auth/refresh').then(res => {
      refreshPromise = null;
      return res.data.accessToken;
    });
  }
  return refreshPromise;
}
```

## MFA Flow

```
User                    Frontend                  Backend
  |-- Login ------------>|-- POST /auth/login ---->|
  |                      |<-- 202: { mfaRequired,  |
  |                      |    sessionId, methods } -|
  |<-- Show MFA page ----|                          |
  |-- Enter code ------->|-- POST /auth/mfa/verify >|
  |                      |<-- 200: { accessToken } -|
  |<-- Redirect ---------|                          |
```

## AuthProvider

```tsx
// Context provides:
interface AuthContext {
  user: User | null;            // Decoded from JWT
  isAuthenticated: boolean;
  isLoading: boolean;           // True during initial token check
  permissions: string[];        // Flat array from JWT
  hasPermission: (p: string) => boolean;
  hasAnyPermission: (...p: string[]) => boolean;
  login: (credentials: LoginInput) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
}
```

### Initial Load

On app start (root layout mount):
1. Try `POST /auth/refresh` (cookie may still be valid)
2. If success → set access token, decode user, authenticated
3. If failure → user is not logged in, redirect to `/login` for protected routes

## Route Protection

```tsx
// In (dashboard)/layout.tsx
export default function DashboardLayout({ children }) {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) return <FullPageSpinner />;
  if (!isAuthenticated) redirect('/login');
  
  return <DashboardShell>{children}</DashboardShell>;
}
```

### Permission-Based Route Protection

```tsx
// In a specific page
export default function MonitoringSettingsPage() {
  return (
    <PermissionGate 
      permission="monitoring:configure" 
      fallback={<PermissionGate permission="monitoring:view-settings" fallback={<Forbidden />}>
        <MonitoringSettings readOnly />
      </PermissionGate>}
    >
      <MonitoringSettings />
    </PermissionGate>
  );
}
```

## Logout

```
1. POST /auth/logout (revokes refresh token server-side)
2. Clear access token from memory
3. Clear any Zustand stores
4. Clear TanStack Query cache
5. Redirect to /login
```

## Session Timeout

- Frontend tracks last user interaction time
- After 30 minutes idle → show "Session expiring" modal (60s countdown)
- If no interaction → logout automatically
- Any API call extends the session server-side

## Related

- [[frontend/cross-cutting/authentication|Authentication]]
- [[security/auth-architecture|Auth Architecture]]
- [[modules/auth/session-management/overview|Session Management]]
- [[modules/auth/mfa/overview|MFA]]
- [[frontend/data-layer/api-integration|API Integration]]
