# Authentication & Authorization Architecture: ONEVO

## Customer Web Authentication

Customer-facing browser sessions use a BFF-style HttpOnly cookie model. Browser JavaScript never receives, stores, decodes, or sends the tenant user JWT.

```text
User                    Frontend                  Auth Module              Database
  |                        |                          |                       |
  |-- Enter credentials -->|                          |                       |
  |                        |-- POST /auth/login ----->|                       |
  |                        |   credentials: include   |-- Verify password --->|
  |                        |                          |<-- User + roles ------|
  |                        |                          |-- Create session ---->|
  |                        |                          |-- Create backend-held |
  |                        |                          |   auth state/JWT      |
  |                        |<-- Set-Cookie + ---------|                       |
  |                        |   safe session metadata  |                       |
  |<-- Redirect dashboard -|                          |                       |
```

The backend may use short-lived tenant JWTs internally, but those JWTs do not leave the backend for browser web sessions.

## Session Lifecycle

| Item | Type | Lifetime | Storage | Refresh |
|:-----|:-----|:---------|:--------|:--------|
| Web session | Server-side session or backend-held token binding | Server controlled | HttpOnly Secure SameSite cookie + `sessions` table | Rotated/extended by backend |
| CSRF token | Random nonce | Server controlled | Readable CSRF cookie + `X-CSRF-Token` header | Rotated by backend |
| Internal tenant token | JWT or equivalent backend credential | Short-lived | Backend only | Recreated by backend |
| Device token | JWT | Agent policy controlled | Windows DPAPI/Credential Manager | Agent refresh flow |
| IDE token | JWT/OAuth token | IDE policy controlled | VS Code SecretStorage | IDE refresh flow |

## Internal Tenant JWT Shape

When the backend uses an internal tenant JWT, it follows the normal ONEVO tenant claims model:

```json
{
  "header": { "alg": "RS256", "typ": "JWT", "kid": "key-id" },
  "payload": {
    "sub": "user-uuid",
    "tenant_id": "tenant-uuid",
    "email": "user@company.com",
    "permissions": ["employees:read", "leave:approve"],
    "perm_ver": 3,
    "iat": 1679616000,
    "exp": 1679616900,
    "iss": "onevo",
    "aud": "onevo-api"
  }
}
```

This token is backend-held for browser sessions. Non-browser clients may receive JWTs only when their own contracts explicitly require it.

## Session Refresh

```text
1. Browser session reaches refresh window.
2. Frontend calls POST /auth/refresh with credentials: include.
3. Browser sends HttpOnly session cookie automatically.
4. Auth module validates server-side session/refresh state.
5. Backend rotates session/refresh state and recreates backend-held auth state if needed.
6. Backend returns safe session metadata and sets a rotated HttpOnly cookie.
```

If a revoked session/refresh chain is used, the backend revokes the whole chain and forces re-login.

## Authorization Model

ONEVO uses permissions and module entitlements, not fixed role names. Tenant roles are customer-defined and must not be hard-coded.

### Permission Format

`{resource}:{action}`

Examples:

```text
employees:read
employees:write
leave:create
leave:approve
attendance:read-own
exceptions:manage
monitoring:configure
roles:manage
settings:admin
```

### Authorization Check

```csharp
[RequirePermission("employees:read")]
public async Task<IResult> GetEmployees(...)
{
    // Middleware already verified:
    // 1. Session cookie is valid
    // 2. Backend-held auth state is valid
    // 3. User has employees:read
    // 4. Tenant context is set
}
```

The frontend may hide UI based on permission metadata, but the backend is always authoritative.

## Permission Revocation

Backend-held auth state can contain permissions captured at issue time. ONEVO uses a permission version counter so permission changes propagate quickly.

```text
On permission grant/revoke/role change:
  INCR perm_version:{user_id}
  Log audit event

On login/session refresh:
  Read effective permissions from DB
  Read current perm_version
  Store permissions and perm_ver in backend-held auth state

On authenticated request:
  Resolve backend-held auth state from HttpOnly session cookie
  Compare auth state's perm_ver against Redis perm_version
  If stale, refresh server-side permission state or reject with 401
```

The browser does not decode JWT claims for permissions. It receives permission metadata from `/auth/session`, `/auth/refresh`, or `/auth/me/permissions`.

## Device JWT

Desktop agents use a separate device-level JWT. This is not the same as customer web session auth.

```json
{
  "payload": {
    "sub": "device-uuid",
    "tenant_id": "tenant-uuid",
    "type": "agent",
    "iat": 1679616000,
    "exp": 1679702400,
    "iss": "onevo",
    "aud": "onevo-agent"
  }
}
```

- Issued at agent registration.
- Contains device and tenant identity, not user permissions.
- Stored by the agent using OS secure storage.
- Used only on `/api/v1/agent/*`.

## Password Security

| Policy | Value |
|:-------|:------|
| Hashing | BCrypt with work factor 12 for backend password hashes |
| Min length | 12 characters |
| Complexity | 1 uppercase, 1 lowercase, 1 digit, 1 special character |
| Rate limiting | 5 attempts/minute per IP |
| Account lockout | 10 failed attempts, 30 minute lockout |
| Password reset | Token-based, 1 hour expiry, single use |
| History | Cannot reuse last 5 passwords |

## MFA Support

- **TOTP authenticator app** - primary Phase 1 MFA method. Secrets are encrypted at rest, users confirm setup with a current 6-digit authenticator code, and replay inside the accepted window is rejected.
- **Email OTP fallback** - fallback/recovery only when tenant policy permits it. Customer release requires delivery through the notification service.
- **Recovery codes** - one-time use codes stored as hashes.

## Session Security

| Setting | Value | Reason |
|:--------|:------|:-------|
| Cookie `HttpOnly` | `true` | Prevents JavaScript from reading the session |
| Cookie `Secure` | `true` | Only sent over HTTPS |
| Cookie `SameSite` | `Strict` or `Lax` by route need | Reduces CSRF exposure |
| CSRF header | Required on mutations | Protects cookie-authenticated writes |
| Session rotation | Login, refresh, role change, privilege change | Limits replay risk |
| Idle timeout | 30 minutes | Limits exposure window |
| Absolute timeout | 24 hours | Forces re-authentication |
| Device tracking | `sessions.device_type` + `ip_address` | Anomaly detection |

## Related

- [[frontend/cross-cutting/authentication|Authentication]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[modules/auth/mfa/overview|MFA]]
- [[modules/auth/session-management/overview|Session Management]]
- [[modules/agent-gateway/agent-server-protocol|Agent Server Protocol]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/compliance|Compliance]]
- [[security/data-classification|Data Classification]]
