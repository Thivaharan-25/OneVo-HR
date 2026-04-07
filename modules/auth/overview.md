# Module: Auth & Security

**Namespace:** `ONEVO.Modules.Auth`
**Pillar:** 1 — HR Management
**Owner:** Dev 2 (Week 1)
**Tables:** 8
**Task File:** [[WEEK1-auth-security]]

---

## Purpose

Handles authentication (JWT RS256), authorization (RBAC with 90+ permissions), session management, MFA, audit logging, and GDPR consent tracking. Provides the security backbone for the entire platform.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[infrastructure]] | `IUserService` | User identity |
| **Consumed by** | All modules | `ICurrentUser`, `RequirePermissionAttribute` | Auth context |
| **Consumed by** | [[agent-gateway]] | `ITokenService` | Device JWT issuance |

---

## Public Interface

```csharp
public interface IAuthService
{
    Task<Result<TokenPairDto>> LoginAsync(LoginCommand command, CancellationToken ct);
    Task<Result<TokenPairDto>> RefreshTokenAsync(string refreshToken, CancellationToken ct);
    Task<Result> LogoutAsync(CancellationToken ct);
    Task<Result> EnableMfaAsync(Guid userId, CancellationToken ct);
    Task<Result<TokenPairDto>> VerifyMfaAsync(Guid userId, string code, CancellationToken ct);
}

public interface ITokenService
{
    Task<string> GenerateAccessTokenAsync(Guid userId, Guid tenantId, List<string> permissions, CancellationToken ct);
    Task<string> GenerateDeviceTokenAsync(Guid deviceId, Guid tenantId, CancellationToken ct); // For agent gateway
    Task<string> GenerateRefreshTokenAsync(Guid userId, CancellationToken ct);
}

public interface IRoleService
{
    Task<Result<RoleDto>> CreateRoleAsync(CreateRoleCommand command, CancellationToken ct);
    Task<Result> AssignRoleAsync(Guid userId, Guid roleId, CancellationToken ct);
}
```

---

## Database Tables (8)

### `roles`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(50)` | e.g., "HR Manager", "CEO", "Employee" |
| `description` | `varchar(255)` | |
| `is_system` | `boolean` | System roles can't be deleted |
| `created_at` | `timestamptz` | |

### `permissions`

Global permission definitions — NOT tenant-scoped.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `code` | `varchar(50)` | e.g., `employees:read`, `workforce:view`, `exceptions:manage` |
| `description` | `varchar(255)` | |
| `module` | `varchar(50)` | Which module this permission belongs to |

**Includes all Workforce Intelligence permissions:** `workforce:view`, `workforce:manage`, `exceptions:view`, `exceptions:manage`, `exceptions:acknowledge`, `monitoring:configure`, `monitoring:view-settings`, `agent:register`, `agent:manage`, `agent:view-health`, `analytics:view`, `analytics:export`, `verification:view`, `verification:configure`

### `role_permissions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `role_id` | `uuid` | FK → roles |
| `permission_id` | `uuid` | FK → permissions |
| PK: `(role_id, permission_id)` | | |

### `user_roles`

| Column | Type | Notes |
|:-------|:-----|:------|
| `user_id` | `uuid` | FK → users |
| `role_id` | `uuid` | FK → roles |
| `assigned_at` | `timestamptz` | |
| PK: `(user_id, role_id)` | | |

### `sessions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `user_id` | `uuid` | FK → users |
| `tenant_id` | `uuid` | FK → tenants |
| `ip_address` | `varchar(45)` | |
| `user_agent` | `varchar(500)` | |
| `started_at` | `timestamptz` | |
| `last_activity_at` | `timestamptz` | |
| `expires_at` | `timestamptz` | |
| `is_revoked` | `boolean` | |

### `refresh_tokens`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `user_id` | `uuid` | FK → users |
| `token_hash` | `varchar(128)` | SHA-256 hash of token |
| `expires_at` | `timestamptz` | 7 days from creation |
| `replaced_by_id` | `uuid` | Self-referencing — token rotation |
| `revoked_at` | `timestamptz` | Nullable |
| `created_at` | `timestamptz` | |

### `audit_logs`

Append-only audit trail. Partitioned by month via `pg_partman`.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `user_id` | `uuid` | FK → users (nullable for system actions) |
| `action` | `varchar(100)` | e.g., `employee.created`, `leave.approved` |
| `resource_type` | `varchar(50)` | e.g., `Employee`, `LeaveRequest` |
| `resource_id` | `uuid` | |
| `old_values_json` | `jsonb` | Previous state |
| `new_values_json` | `jsonb` | New state |
| `ip_address` | `varchar(45)` | |
| `correlation_id` | `uuid` | Request correlation |
| `created_at` | `timestamptz` | |

### `gdpr_consent_records`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `user_id` | `uuid` | FK → users |
| `consent_type` | `varchar(50)` | `data_processing`, `biometric`, `monitoring`, `marketing` |
| `consented` | `boolean` | |
| `consented_at` | `timestamptz` | |
| `ip_address` | `varchar(45)` | |

---

## Key Business Rules

1. **JWT RS256** — access tokens (15 min), refresh tokens (7 days) with rotation.
2. **Device JWT** for agents — contains `device_id` + `tenant_id` + `type: "agent"` claim. No user permissions.
3. **Refresh token rotation** — each use generates a new token, old one is marked with `replaced_by_id`. If a revoked token is reused, revoke the entire chain (token theft detection).
4. **GDPR consent for monitoring** — `consent_type: "monitoring"` must be recorded before monitoring features activate for an employee.
5. **Audit logs are append-only** — partitioned by month, never deleted (compliance requirement).

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| POST | `/api/v1/auth/login` | Public | Login |
| POST | `/api/v1/auth/refresh` | Public | Refresh access token |
| POST | `/api/v1/auth/logout` | Authenticated | Logout |
| POST | `/api/v1/auth/mfa/enable` | Authenticated | Enable MFA |
| POST | `/api/v1/auth/mfa/verify` | Authenticated | Verify MFA code |
| GET | `/api/v1/roles` | `roles:read` | List roles |
| POST | `/api/v1/roles` | `roles:manage` | Create role |
| PUT | `/api/v1/roles/{id}` | `roles:manage` | Update role |
| POST | `/api/v1/roles/{id}/permissions` | `roles:manage` | Assign permissions |
| GET | `/api/v1/audit-logs` | `settings:admin` | Query audit logs |

## Features

- [[authentication]] — JWT RS256 login, token issuance, refresh token rotation
- [[authorization]] — RBAC, 90+ permissions across all modules
- [[session-management]] — Session tracking, revocation, expiry
- [[mfa]] — Multi-factor authentication (TOTP)
- [[audit-logging]] — Append-only audit trail, partitioned by month
- [[gdpr-consent]] — Consent tracking for data processing and monitoring

---

## Related

- [[auth-architecture]] — Full JWT RS256 design, device JWT, token rotation
- [[multi-tenancy]] — All roles and sessions are tenant-scoped
- [[compliance]] — Audit logs are never deleted; GDPR consent records
- [[data-classification]] — Refresh tokens hashed (SHA-256), never stored raw
- [[shared-kernel]] — `ICurrentUser`, `RequirePermissionAttribute` used by all modules
- [[logging-standards]] — Correlation IDs in audit logs
- [[WEEK1-auth-security]] — Implementation task file

See also: [[module-catalog]], [[infrastructure]], [[auth-architecture]], [[compliance]]
