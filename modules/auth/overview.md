# Module: Auth & Security

**Namespace:** `ONEVO.Modules.Auth`
**Phase:** 1 — Build
**Pillar:** 1 — HR Management
**Owner:** Dev 2 (Week 1)
**Tables:** 11
**Task File:** [[current-focus/DEV2-auth-security|DEV2: Auth Security]]

---

## Purpose

Handles authentication (JWT RS256), authorization (**hybrid permission control** with 90+ permissions, per-employee overrides, hierarchy-scoped access), session management, MFA, audit logging, and GDPR consent tracking. Provides the security backbone for the entire platform.

**Authorization model:** NOT role-based. Roles are convenience templates. Super Admin grants feature/module access to any role or individual employee. Per-employee permission overrides (grant/revoke) always win over role defaults. All data access is scoped to the user's position in the org hierarchy (they only see employees below them).

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[modules/infrastructure/overview\|Infrastructure]] | `IUserService` | User identity |
| **Consumed by** | All modules | `ICurrentUser`, `RequirePermissionAttribute` | Auth context |
| **Consumed by** | [[modules/agent-gateway/overview\|Agent Gateway]] | `ITokenService` | Device JWT issuance |

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
    /// Bridge JWT: aud="onevo-bridge", type="bridge", bridges=[...], expires 1 hour
    Task<string> GenerateBridgeTokenAsync(Guid clientId, Guid tenantId, string[] allowedBridges, CancellationToken ct);
}

public interface IRoleService
{
    Task<Result<RoleDto>> CreateRoleAsync(CreateRoleCommand command, CancellationToken ct);
    Task<Result> AssignRoleAsync(Guid userId, Guid roleId, CancellationToken ct);
}

public interface IPermissionResolver
{
    /// Resolves effective permissions: role permissions + individual overrides, filtered by feature grants
    Task<List<string>> ResolveAsync(Guid userId, Guid tenantId, CancellationToken ct);
}

public interface IHierarchyScopeService
{
    /// Returns a HierarchyFilter value object for the current user.
    /// Super Admin → HierarchyFilter.All (no restriction, no CTE)
    /// Manager (employees:read-team) → HierarchyFilter.SubordinatesOf(managerId)
    /// Employee → HierarchyFilter.OwnOnly(employeeId)
    /// Pass the filter into repository methods — never materialize a list of IDs.
    Task<HierarchyFilter> GetFilterAsync(CancellationToken ct);
}

public interface IFeatureAccessService
{
    /// Grants module access to a role or individual employee
    Task<Result> GrantAsync(GrantFeatureAccessCommand command, CancellationToken ct);
    /// Checks if a module is granted for a specific user (checks both role-level and employee-level grants)
    Task<bool> IsModuleGrantedAsync(Guid userId, string module, CancellationToken ct);
}

public interface IPermissionOverrideService
{
    /// Sets a grant or revoke override for a specific permission on a specific employee
    Task<Result> SetAsync(Guid userId, SetPermissionOverrideCommand command, CancellationToken ct);
}

public interface IBridgeAuthService
{
    /// Validates client_id + client_secret, issues a bridge JWT scoped to allowed bridges.
    /// Used by WorkManage Pro for service-to-service authentication.
    Task<Result<BridgeTokenDto>> IssueTokenAsync(BridgeTokenRequest request, CancellationToken ct);
}
```

---

## Database Tables (10)

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
| `assigned_by` | `uuid` | FK → users (who granted this) |
| PK: `(user_id, role_id)` | | |

### `user_permission_overrides`

Per-employee permission overrides. Super Admin can grant or revoke individual permissions for any employee, independent of their role. **Overrides always win over role permissions.**

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `user_id` | `uuid` | FK → users |
| `permission_id` | `uuid` | FK → permissions |
| `grant_type` | `varchar(10)` | `grant` or `revoke` |
| `reason` | `varchar(255)` | Why this override exists |
| `granted_by` | `uuid` | FK → users (Super Admin who set this) |
| `created_at` | `timestamptz` | |
| UNIQUE: `(tenant_id, user_id, permission_id)` | | |

### `feature_access_grants`

Module-level access grants. Super Admin toggles entire feature modules for a role or individual employee.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `grantee_type` | `varchar(10)` | `role` or `employee` |
| `grantee_id` | `uuid` | FK → roles.id OR users.id |
| `module` | `varchar(50)` | Module code: `leave`, `payroll`, `performance`, etc. |
| `is_enabled` | `boolean` | |
| `granted_by` | `uuid` | FK → users |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |
| UNIQUE: `(tenant_id, grantee_type, grantee_id, module)` | | |

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

### `bridge_clients`

Service-to-service OAuth clients for bridge API access (WorkManage Pro and future integrations).

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK — this is the `client_id` |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(100)` | Human-readable name (e.g., "WorkManage Pro") |
| `client_secret_hash` | `varchar(255)` | Argon2id hash — secret shown once at registration |
| `allowed_bridges` | `text[]` | Bridge names this client may call (e.g., `["people-sync", "availability"]`) |
| `is_active` | `boolean` | Admin can revoke access by setting false |
| `created_by` | `uuid` | FK → users (Super Admin who registered this client) |
| `created_at` | `timestamptz` | |
| `last_used_at` | `timestamptz` | Updated on each successful token issuance |

UNIQUE: `(tenant_id, name)` — one client per integration per tenant.

---

## Domain Events (intra-module — MediatR)

> These events are published and consumed within this module only. They never leave the module.

| Event | Published When | Handler |
|:------|:---------------|:--------|
| _(none)_ | — | — |

## Integration Events (cross-module — RabbitMQ)

### Publishes

| Event | Routing Key | Published When | Consumers |
|:------|:-----------|:---------------|:----------|
| `UserLoggedIn` | `auth.login` | User successfully authenticates | [[modules/shared-platform/overview\|Shared Platform]] (session tracking) |
| `UserLoggedOut` | `auth.logout` | User logs out or session expires | [[modules/shared-platform/overview\|Shared Platform]] |
| `RoleAssigned` | `auth.role` | Role assigned to a user | Downstream permission consumers |
| `PermissionChanged` | `auth.permission` | Individual permission override set or removed | Downstream permission consumers |

### Consumes

| Event | Routing Key | Source Module | Action Taken |
|:------|:-----------|:-------------|:-------------|
| `UserStatusChanged` | `infrastructure.user.status` | [[modules/infrastructure/overview\|Infrastructure]] | Activate or deactivate user login access |

---

## Key Business Rules

1. **JWT RS256** — access tokens (15 min), refresh tokens (7 days) with rotation.
2. **Hybrid permission control** — roles are templates; effective permissions = role permissions + individual overrides; filtered by feature grants; scoped by org hierarchy.
3. **Hierarchy scoping** — users only see/manage employees below them in the reporting chain (`employees.reports_to_id`). Super Admin bypasses hierarchy.
4. **Never hardcode role names** — roles are custom, created by Super Admin. Always check permissions, never role names.
5. **Device JWT** for agents — contains `device_id` + `tenant_id` + `type: "agent"` claim. No user permissions.
6. **Refresh token rotation** — each use generates a new token, old one is marked with `replaced_by_id`. If a revoked token is reused, revoke the entire chain (token theft detection).
7. **GDPR consent for monitoring** — `consent_type: "monitoring"` must be recorded before monitoring features activate for an employee.
8. **Audit logs are append-only** — partitioned by month, never deleted (compliance requirement).
9. **Bridge JWT is separate from user JWT** — `aud: "onevo-bridge"`, `type: "bridge"`. Bridge middleware rejects user JWTs on `/api/v1/bridges/*` and user endpoints reject bridge JWTs. A single client secret grants access only to the bridges listed in `bridge_clients.allowed_bridges`.

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| POST | `/api/v1/auth/login` | Public | Login |
| POST | `/api/v1/auth/refresh` | Public | Refresh access token |
| POST | `/api/v1/auth/logout` | Authenticated | Logout |
| POST | `/api/v1/auth/bridge/token` | Public | Issue bridge JWT (OAuth client credentials) |
| POST | `/api/v1/auth/mfa/enable` | Authenticated | Enable MFA |
| POST | `/api/v1/auth/mfa/verify` | Authenticated | Verify MFA code |
| GET | `/api/v1/roles` | `roles:read` | List roles |
| POST | `/api/v1/roles` | `roles:manage` | Create role |
| PUT | `/api/v1/roles/{id}` | `roles:manage` | Update role |
| POST | `/api/v1/roles/{id}/permissions` | `roles:manage` | Set role permissions |
| POST | `/api/v1/users/{id}/roles` | `roles:manage` | Assign role to employee |
| GET | `/api/v1/users/{id}/permissions` | `roles:manage` | Get effective permissions |
| POST | `/api/v1/users/{id}/permission-overrides` | `roles:manage` | Grant/revoke permission override |
| DELETE | `/api/v1/users/{id}/permission-overrides/{permId}` | `roles:manage` | Remove override |
| GET | `/api/v1/feature-access` | `roles:manage` | List feature grants |
| POST | `/api/v1/feature-access` | `roles:manage` | Grant feature to role/employee |
| DELETE | `/api/v1/feature-access/{id}` | `roles:manage` | Revoke feature grant |
| GET | `/api/v1/audit-logs` | `settings:admin` | Query audit logs |

## Features

- [[frontend/cross-cutting/authentication|Authentication]] — JWT RS256 login, token issuance, refresh token rotation
- [[frontend/cross-cutting/authorization|Authorization]] — Hybrid permission control: roles + per-employee overrides + feature grants + hierarchy scoping
- [[modules/auth/session-management/overview|Session Management]] — Session tracking, revocation, expiry
- [[mfa]] — Multi-factor authentication (TOTP)
- [[modules/auth/audit-logging/overview|Audit Logging]] — Append-only audit trail, partitioned by month
- [[Userflow/Auth-Access/gdpr-consent|Gdpr Consent]] — Consent tracking for data processing and monitoring

---

## Related

- [[security/auth-architecture|Auth Architecture]] — Full JWT RS256 design, device JWT, token rotation
- [[infrastructure/multi-tenancy|Multi Tenancy]] — All roles and sessions are tenant-scoped
- [[security/compliance|Compliance]] — Audit logs are never deleted; GDPR consent records
- [[security/data-classification|Data Classification]] — Refresh tokens hashed (SHA-256), never stored raw
- [[backend/shared-kernel|Shared Kernel]] — `ICurrentUser`, `RequirePermissionAttribute` used by all modules
- [[code-standards/logging-standards|Logging Standards]] — Correlation IDs in audit logs
- [[current-focus/DEV2-auth-security|DEV2: Auth Security]] — Implementation task file

See also: [[backend/module-catalog|Module Catalog]], [[modules/infrastructure/overview|Infrastructure]], [[security/auth-architecture|Auth Architecture]], [[security/compliance|Compliance]]
