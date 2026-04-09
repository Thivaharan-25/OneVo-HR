# Authentication (Frontend)

## Auth Flow

```
┌─ Login Page ─────────────────────────────────────────────────┐
│                                                               │
│  1. User enters email + password                              │
│  2. POST /api/v1/auth/login                                   │
│     Response: { accessToken, user, mfaRequired? }             │
│                                                               │
│  ├── mfaRequired = true → redirect to /mfa                   │
│  │   3. User enters TOTP code                                │
│  │   4. POST /api/v1/auth/mfa/verify                         │
│  │      Response: { accessToken, refreshToken (HttpOnly) }   │
│  │                                                            │
│  └── mfaRequired = false → tokens returned directly          │
│                                                               │
│  5. Store access token in memory (NOT localStorage)           │
│  6. Refresh token set as HttpOnly cookie by server            │
│  7. Redirect to /overview (or ?redirect= target)             │
└───────────────────────────────────────────────────────────────┘
```

## Token Management

| Token | Storage | Lifetime | Sent As |
|:------|:--------|:---------|:--------|
| Access Token | In-memory (Zustand) | 15 min | `Authorization: Bearer {token}` header |
| Refresh Token | HttpOnly Secure cookie | 7 days | Automatic via `credentials: 'include'` |

### Why In-Memory for Access Token

- XSS cannot read in-memory state (unlike localStorage)
- Token is lost on page refresh → silent refresh via refresh token
- No `window.accessToken` global — encapsulated in AuthStore

### Silent Refresh

On app load and when access token expires:

```tsx
// lib/auth.ts
let accessToken: string | null = null;

export function getAccessToken(): string | null {
  return accessToken;
}

export async function refreshToken(): Promise<boolean> {
  try {
    const response = await fetch(`${API_URL}/api/v1/auth/refresh`, {
      method: 'POST',
      credentials: 'include', // Sends HttpOnly refresh cookie
    });

    if (!response.ok) return false;

    const data = await response.json();
    accessToken = data.accessToken;
    useAuthStore.getState().setUser(data.user, data.permissions);
    return true;
  } catch {
    return false;
  }
}

// Called on app mount
export async function initializeAuth(): Promise<boolean> {
  return refreshToken(); // Try to get a new access token from refresh cookie
}
```

### Proactive Refresh

Refresh before expiry to avoid failed requests:

```tsx
// Schedule refresh 1 minute before expiry
function scheduleRefresh(token: string) {
  const payload = decodeJwt(token);
  const expiresAt = payload.exp * 1000;
  const refreshAt = expiresAt - 60_000; // 1 min before
  const delay = refreshAt - Date.now();

  if (delay > 0) {
    setTimeout(() => refreshToken(), delay);
  }
}
```

## Auth Provider

```tsx
// components/providers/auth-provider.tsx
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isLoading, setIsLoading] = useState(true);
  const { user, setUser } = useAuthStore();

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
// stores/use-auth-store.ts
interface AuthState {
  user: User | null;
  permissions: string[];
  tenantId: string | null;
  isAuthenticated: boolean;
  setUser: (user: User, permissions: string[]) => void;
  clear: () => void;
  hasPermission: (permission: string) => boolean;
  hasAnyPermission: (...permissions: string[]) => boolean;
  hasAllPermissions: (...permissions: string[]) => boolean;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  permissions: [],
  tenantId: null,
  isAuthenticated: false,

  setUser: (user, permissions) => set({
    user,
    permissions,
    tenantId: user.tenantId,
    isAuthenticated: true,
  }),

  clear: () => set({
    user: null,
    permissions: [],
    tenantId: null,
    isAuthenticated: false,
  }),

  hasPermission: (permission) => get().permissions.includes(permission),
  hasAnyPermission: (...perms) => perms.some(p => get().permissions.includes(p)),
  hasAllPermissions: (...perms) => perms.every(p => get().permissions.includes(p)),
}));
```

## Logout

```tsx
async function logout() {
  // 1. Call API to invalidate refresh token server-side
  await api.auth.logout();

  // 2. Clear client state
  accessToken = null;
  useAuthStore.getState().clear();
  queryClient.clear(); // Wipe all cached data

  // 3. Stop SignalR
  signalRConnection?.stop();

  // 4. Redirect to login
  window.location.href = '/login';
}
```

## Multi-Tab Session Sync

```tsx
// Broadcast channel to sync auth state across tabs
const authChannel = new BroadcastChannel('auth');

authChannel.onmessage = (event) => {
  if (event.data.type === 'LOGOUT') {
    // Another tab logged out — clear this tab too
    useAuthStore.getState().clear();
    window.location.href = '/login';
  }
  if (event.data.type === 'TOKEN_REFRESHED') {
    // Another tab refreshed — update this tab's token
    accessToken = event.data.accessToken;
  }
};

// On logout, broadcast to other tabs
function logout() {
  authChannel.postMessage({ type: 'LOGOUT' });
  // ... rest of logout
}
```

## Related

- [[frontend/cross-cutting/authorization|Authorization]] — RBAC permission system
- [[frontend/cross-cutting/security|Security]] — XSS, CSRF protection
- [[frontend/data-layer/api-integration|Api Integration]] — API client auth interceptor
- [[frontend/architecture/routing|Routing]] — route guards
