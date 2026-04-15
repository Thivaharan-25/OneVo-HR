# Authentication & Authorization Architecture: ONEVO

## Authentication Flow

### Login Flow

```
User                    Frontend                  Auth Module              Database
  |                        |                          |                       |
  |-- Enter credentials -->|                          |                       |
  |                        |-- POST /auth/login ------>|                       |
  |                        |                          |-- Verify password     |
  |                        |                          |   (Argon2id) -------->|
  |                        |                          |<-- User + Roles ------|
  |                        |                          |-- Generate JWT (RS256)|
  |                        |                          |-- Create session ---->|
  |                        |<-- Access token + --------|                       |
  |                        |   Refresh token (cookie)  |                       |
  |<-- Redirect to --------|                          |                       |
  |   dashboard            |                          |                       |
```

### Token Lifecycle

| Token | Type | Lifetime | Storage | Refresh |
|:------|:-----|:---------|:--------|:--------|
| Access token | JWT (RS256) | 15 minutes | Memory (frontend) | Via refresh token |
| Refresh token | Opaque (hashed in DB) | 7 days | HttpOnly Secure cookie | Rotated on use |
| Session | UUID | 24 hours | `sessions` table | Extended on activity |

### JWT Structure

```json
{
  "header": { "alg": "RS256", "typ": "JWT", "kid": "key-id" },
  "payload": {
    "sub": "user-uuid",
    "tenant_id": "tenant-uuid",
    "email": "user@company.com",
    "roles": ["HR_Admin", "Manager"],
    "permissions": ["employees:read", "employees:write", "leave:approve", "leave:read"],
    "iat": 1679616000,
    "exp": 1679616900,
    "iss": "onevo",
    "aud": "onevo-api"
  }
}
```

### JWT Key Rotation

Dual-key 24-hour rotation window:

1. Generate new RSA key pair
2. Sign new tokens with new key, verify with both old + new keys
3. After 24 hours, retire old key
4. Users don't need to re-login during rotation

### Refresh Token Rotation

```
1. Access token expires
2. Frontend sends refresh token cookie to POST /auth/refresh
3. Auth module validates: token_hash matches, not expired, not revoked
4. Generate new access token + NEW refresh token
5. Revoke old refresh token (is_revoked = true)
6. Link old → new via replaced_by_id (chain for audit)
7. Return new tokens
```

If a revoked refresh token is used (replay attack), revoke the entire chain and force re-login.

## Authorization Model (RBAC)

### Role Hierarchy

```
Employee (base) → Manager → HR Admin → Org Owner → System Admin
```

| Role | Scope | Default Permissions |
|:-----|:------|:-------------------|
| `Employee` | Own data | `employees:read-own`, `leave:read-own`, `leave:create`, `attendance:read-own` |
| `Manager` | Team data | Employee permissions + `employees:read-team`, `leave:approve`, `attendance:read-team`, `performance:read-team`, `workforce:view`, `exceptions:view`, `exceptions:acknowledge`, `analytics:view` |
| `HR_Admin` | Org data | Manager permissions + `employees:write`, `leave:manage`, `payroll:read`, `performance:manage`, `grievance:manage`, `workforce:manage`, `exceptions:manage`, `monitoring:configure`, `monitoring:view-settings`, `analytics:export`, `verification:view`, `verification:configure`, `agent:manage`, `agent:view-health` |
| `Org_Owner` | Full org | HR Admin + `settings:admin`, `billing:manage`, `roles:manage` |
| `System_Admin` | System | Everything (system role, not assignable per tenant) |

### Permission Format

`{resource}:{action}`

90+ permissions covering:

```
// HR Management
employees:read, employees:write, employees:delete, employees:read-own, employees:read-team
leave:read, leave:create, leave:approve, leave:manage, leave:read-own
attendance:read, attendance:write, attendance:approve, attendance:read-own, attendance:read-team
payroll:read, payroll:write, payroll:run, payroll:approve
performance:read, performance:write, performance:manage, performance:read-team
skills:read, skills:write, skills:validate, skills:manage
documents:read, documents:write, documents:manage
grievance:read, grievance:write, grievance:manage
expense:read, expense:create, expense:approve, expense:manage
reports:read, reports:create, reports:manage

// Workforce Intelligence (NEW)
workforce:view, workforce:manage
exceptions:view, exceptions:manage, exceptions:acknowledge
monitoring:configure, monitoring:view-settings
agent:register, agent:manage, agent:view-health
analytics:view, analytics:export
verification:view, verification:configure

// System
notifications:read, notifications:manage
settings:read, settings:admin
billing:read, billing:manage
roles:read, roles:manage
users:read, users:manage
```

### Device JWT (Agent Gateway)

Desktop agents use a separate device-level JWT. This is NOT the same as user JWT.

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

- Issued at agent registration (`POST /api/v1/agent/register`)
- Contains `device_id` + `tenant_id` but **NO user permissions**
- The `type: "agent"` claim distinguishes from user JWT
- Employee context linked at login via MAUI tray app
- See [[modules/agent-gateway/overview|Agent Gateway]] for full protocol

### Authorization Check

```csharp
[RequirePermission("employees:read")]
public async Task<IResult> GetEmployees(...)
{
    // Middleware already verified:
    // 1. JWT is valid
    // 2. User has "employees:read" permission
    // 3. Tenant context is set
    
    // Service-level: additional data-scoping based on role
    var scope = _currentUser.HasPermission("employees:read-team") 
        ? DataScope.Team 
        : DataScope.Own;
    
    var employees = await _employeeService.GetEmployeesAsync(scope, ct);
    return Results.Ok(employees);
}
```

### Time-Bound Roles

Roles can have `expires_at` for temporary access:

```csharp
// Assign temporary HR Admin role for 30 days
var userRole = new UserRole
{
    UserId = userId,
    RoleId = hrAdminRoleId,
    AssignedBy = currentUserId,
    ExpiresAt = DateTimeOffset.UtcNow.AddDays(30)
};
```

Expired roles are cleaned up by a Hangfire daily job.

### Permission Revocation — Real-Time Propagation

**The problem:** JWTs contain permissions baked-in at issue time. With a 15-minute access token lifetime, a revoked permission remains effective for up to 15 minutes after revocation.

**The solution: Redis Permission Version Counter**

Each user has a version counter in Redis: `perm_version:{user_id}` (integer, default 0).

```
On permission grant or revoke:
  → INCR perm_version:{user_id}   (atomic, TTL: 24h)
  → Log audit event

On JWT issue (login or token refresh):
  → Read current perm_version from Redis
  → Embed as claim: "perm_ver": <current_version>

On every authenticated request (middleware):
  → Read "perm_ver" from JWT
  → GET perm_version:{user_id} from Redis
  → If JWT perm_ver < Redis version → reject with 401 + {"code": "permissions_changed"}
  → Frontend receives 401 → silently refresh access token
  → New JWT issued with fresh permissions from DB + new perm_ver

On token refresh:
  → Re-read all permissions from DB (fresh)
  → GET current perm_version:{user_id} from Redis
  → Embed fresh perm_ver in new JWT
```

**Propagation latency:** Revocation propagates within one request cycle — the next API call after a permission change triggers a 401 → silent refresh → new token with updated permissions. In practice: ≤1 second for active users.

**Redis failure fallback:** If Redis is unavailable (circuit open), fall back to permitting the existing JWT permissions (fail-open). Log a warning. Do NOT fall back to DB permission lookup per request — that defeats the purpose of baking permissions into the JWT. The 15-minute window is acceptable during Redis outages.

| Key | Type | TTL | Set when | Incremented when |
|:----|:-----|:----|:---------|:----------------|
| `perm_version:{user_id}` | String (integer) | 24h (reset on activity) | User first logs in | Any permission grant, revoke, role change, or role expiry |

**Implementation:** `IPermissionVersionService` wraps the Redis calls. Injected into `AuthorizationMiddleware` and `TokenService`.

```csharp
public interface IPermissionVersionService
{
    Task<long> GetCurrentVersionAsync(Guid userId, CancellationToken ct);
    Task<long> IncrementVersionAsync(Guid userId, CancellationToken ct);
}
```

## Password Security

| Policy | Value |
|:-------|:------|
| Hashing | Argon2id (memory: 64MB, iterations: 3, parallelism: 1) |
| Min length | 12 characters |
| Complexity | 1 uppercase, 1 lowercase, 1 digit, 1 special character |
| Rate limiting | 5 attempts/minute per IP |
| Account lockout | 10 failed attempts → 30 min lockout |
| Password reset | Token-based, 1 hour expiry, single use |
| History | Cannot reuse last 5 passwords |

## MFA Support

Multiple methods per user via `user_mfa` table:

- **TOTP** (Google Authenticator, Authy)
- **Email OTP** (6-digit code via Resend)
- **Recovery codes** (one-time use backup codes)

## Session Security

| Setting | Value | Reason |
|:--------|:------|:-------|
| Cookie `HttpOnly` | `true` | Prevents XSS from reading refresh token |
| Cookie `Secure` | `true` | Only sent over HTTPS |
| Cookie `SameSite` | `Strict` | Prevents CSRF |
| Session rotation | On role change | Prevents session fixation |
| Idle timeout | 30 minutes | Limits exposure window |
| Absolute timeout | 24 hours | Forces re-authentication |
| Device tracking | `sessions.device_type` + `ip_address` | Anomaly detection |

## Related

- [[frontend/cross-cutting/authentication|Authentication]]
- [[frontend/cross-cutting/authorization|Authorization]]
- [[mfa]]
- [[modules/auth/session-management/overview|Session Management]]
- [[modules/agent-gateway/agent-server-protocol|Agent Server Protocol]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/compliance|Compliance]]
- [[security/data-classification|Data Classification]]
- [[current-focus/DEV2-auth-security|DEV2: Auth Security]]
