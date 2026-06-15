# Module: Auth & Security

**Feature Folder:** `Application/Features/Auth`
**Phase:** 1 — Build
**Pillar:** 1 — HR Management
**Owner:** Dev 2 (Week 1)
**Tables:** 12
**Task File:** [[current-focus/DEV2-auth-security|DEV2: Auth Security]]

---

## Purpose

Handles customer web authentication through BFF-style HttpOnly cookie sessions, backend-held tenant auth state/JWTs, authorization (**hybrid permission control** with 106 explicitly grantable permissions plus universal auto-grants, role templates, per-employee overrides, temporary grants, hierarchy-scoped access, and hierarchy bypass grants), session management, MFA, audit logging, and Legal & Privacy acceptance tracking. Provides the security backbone for the entire platform.

**Authorization model:** NOT simple RBAC. Roles are tenant-scoped permission bundles created from templates. Developer Platform can create starter role templates during provisioning, but the materialized tenant roles still live in the Auth module. Universal permissions are auto-granted to every active employee and cannot be revoked. Per-employee permission overrides (grant/revoke) always win over role defaults for explicitly grantable permissions when they are inside their valid date window. All data access is scoped to the user's position in the org hierarchy (they only see employees below them), except for explicit hierarchy bypass grants.

**Module entitlement boundary:** role templates, tenant roles, and permission override screens must only expose permissions from modules enabled for the tenant, plus universal permissions. If a tenant has only Employee Management and Leave enabled, Payroll, WorkSync, Workforce Intelligence, Agent Gateway, and other disabled-module permissions cannot be shown or assigned.

**Super Admin boundary:** Platform Super Admin and Tenant Super Admin are different powers. Platform Super Admin is only for Developer Platform / operator routes. Tenant Super Admin / tenant owner means full administration inside the tenant's enabled module catalog only. Tenant Super Admin must not bypass subscription, paid add-on, trial, disabled-module, or module-catalog checks.

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
    Task<Result<AuthSessionDto>> LoginAsync(LoginCommand command, CancellationToken ct);
    Task<Result<AuthSessionDto>> RefreshSessionAsync(string sessionCookie, CancellationToken ct);
    Task<Result> LogoutAsync(CancellationToken ct);
    Task<Result> BeginTotpMfaSetupAsync(Guid userId, CancellationToken ct);
    Task<Result> SendMfaFallbackOtpAsync(Guid userId, CancellationToken ct);
    Task<Result<AuthSessionDto>> VerifyMfaAsync(Guid userId, string code, CancellationToken ct);
}

public interface ITokenService
{
    Task<string> GenerateInternalAccessTokenAsync(Guid userId, Guid tenantId, List<string> permissions, CancellationToken ct);
    Task<string> GenerateDeviceTokenAsync(Guid deviceId, Guid tenantId, CancellationToken ct); // For agent gateway
    Task<string> GenerateRefreshTokenAsync(Guid userId, CancellationToken ct);
}

public interface IRoleService
{
    Task<Result<RoleDto>> CreateRoleAsync(CreateRoleCommand command, CancellationToken ct);
    Task<Result> AssignRoleAsync(Guid userId, Guid roleId, CancellationToken ct);
    Task<Result> SetPermissionsAsync(Guid roleId, IReadOnlyCollection<string> permissionCodes, CancellationToken ct);
}

public interface IRoleTemplateService
{
    Task<IReadOnlyList<RoleTemplateDto>> ListAsync(CancellationToken ct);
    Task<Result<RoleTemplateDto>> CreateAsync(CreateRoleTemplateCommand command, CancellationToken ct);
    Task<Result<RoleDto>> ApplyToTenantAsync(Guid tenantId, Guid templateId, CancellationToken ct);
}

public interface IPermissionResolver
{
    /// Resolves effective permissions from active tenant modules, selected commercial feature keys,
    /// runtime feature flags, universal auto-grants, active roles, valid individual overrides,
    /// optional role/employee feature visibility grants, and tenant-owner expansion.
    /// Commercial entitlement is evaluated before RBAC; Tenant Super Admin cannot access disabled modules
    /// or commercially excluded features.
    Task<List<string>> ResolveAsync(Guid userId, Guid tenantId, CancellationToken ct);
}

public interface IAccessPolicyResolver
{
    /// Resolves the effective access policy for a given (userId, permissionCode, tenantId).
    /// Returns one of: self | direct_reports | reporting_tree | department |
    ///                  department_tree | org_unit_tree | organization
    /// Returns null for tenant-wide permissions that are not employee-record scoped.
    Task<string?> ResolveAsync(Guid userId, string permissionCode, Guid tenantId, CancellationToken ct);
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

```

---

## Code Location (Clean Architecture)

Domain entities:
  ONEVO.Domain/Features/Auth/Entities/
  ONEVO.Domain/Features/Auth/Events/

Application (CQRS):
  ONEVO.Application/Features/Auth/Commands/
  ONEVO.Application/Features/Auth/Queries/
  ONEVO.Application/Features/Auth/DTOs/Requests/
  ONEVO.Application/Features/Auth/DTOs/Responses/
  ONEVO.Application/Features/Auth/Validators/
  ONEVO.Application/Features/Auth/EventHandlers/

Infrastructure:
  ONEVO.Infrastructure/Persistence/Configurations/Auth/

API endpoints:
  ONEVO.Api/Controllers/Auth/AuthController.cs

---

## Database Tables (13)

### `roles`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `name` | `varchar(50)` | e.g., "HR Manager", "CEO", "Employee" |
| `description` | `varchar(255)` | |
| `is_system` | `boolean` | System roles can't be deleted |
| `created_at` | `timestamptz` | |

### `role_templates`

Operator-managed starter role definitions used by the Developer Platform provisioning wizard. Templates are not runtime grants until applied to a tenant.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `name` | `varchar(100)` | e.g., "HR Admin", "Leave Manager" |
| `description` | `varchar(255)` | |
| `module_keys_json` | `jsonb` | Modules covered by this template |
| `permission_codes_json` | `jsonb` | Permission codes included in the template |
| `is_system` | `boolean` | ONEVO default template; clone before tenant-specific changes |
| `version` | `integer` | Incremented when template changes |
| `is_active` | `boolean` | |
| `created_at` | `timestamptz` | |

### `permissions`

Global permission definitions — NOT tenant-scoped.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `code` | `varchar(50)` | e.g., `employees:read`, `workforce:view`, `exceptions:manage` |
| `description` | `varchar(255)` | |
| `module` | `varchar(50)` | Which module this permission belongs to |

**Includes all Workforce Intelligence permissions:** `workforce:view`, `workforce:manage`, `exceptions:view`, `exceptions:manage`, `exceptions:acknowledge`, `monitoring:configure`, `monitoring:view-settings`, `agent:register`, `agent:manage`, `agent:view-health`, `agent:command`, `analytics:view`, `analytics:export`, `verification:view`, `verification:review`, `verification:configure`

### `role_permissions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `role_id` | `uuid` | FK ? roles |
| `permission_id` | `uuid` | FK ? permissions |
| PK: `(role_id, permission_id)` | | |

### `user_roles`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `user_id` | `uuid` | FK → users |
| `role_id` | `uuid` | FK → roles |
| `scope_type` | `varchar(30)` | `Organization`, `Department`, `Team`, `Own`, or `DirectReports` |
| `scope_id` | `uuid` | nullable boundary id for scoped assignments |
| `assigned_at` | `timestamptz` | |
| `assigned_by` | `uuid` | FK → users (who granted this) |
| `expires_at` | `timestamptz` | nullable; use for temporary role assignment |
| UNIQUE: `(tenant_id, user_id, role_id, scope_type, scope_id)` | | |

### `user_permission_overrides`

Per-employee permission overrides. Tenant Super Admin can grant or revoke individual permissions for any employee, independent of their role, but only for permissions in enabled tenant modules. **Overrides always win over role permissions** when active.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `user_id` | `uuid` | FK ? users |
| `permission_id` | `uuid` | FK ? permissions |
| `grant_type` | `varchar(10)` | `grant` or `revoke` |
| `scope_type` | `varchar(30)` | Nullable. Scope for this individual permission override |
| `scope_id` | `uuid` | Nullable boundary id for scoped overrides |
| `reason` | `varchar(255)` | Why this override exists |
| `granted_by` | `uuid` | FK ? users (Tenant Super Admin or delegated permission admin who set this) |
| `valid_from` | `timestamptz` | nullable; default active immediately |
| `expires_at` | `timestamptz` | nullable; use for date/time-bound individual permission |
| `created_at` | `timestamptz` | |
| UNIQUE: `(tenant_id, user_id, permission_id)` | | |

### `feature_access_grants`

Role/employee feature visibility grants inside the tenant's already-commercially-included boundary. These grants cannot enable a module the tenant has not purchased, trialed, or otherwise received through an approved tenant entitlement, and cannot enable a feature absent from the tenant's current subscription/custom contract.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `grantee_type` | `varchar(10)` | `role` or `employee` |
| `grantee_id` | `uuid` | FK → roles.id OR users.id |
| `module` | `varchar(80)` | Module code: `leave`, `work_management`, `chat_ai`, etc. |
| `feature_key` | `varchar(120)` | Nullable commercial feature key; null means module-level visibility |
| `is_enabled` | `boolean` | |
| `granted_by` | `uuid` | FK → users |
| `valid_from` | `timestamptz` | nullable; default active immediately |
| `expires_at` | `timestamptz` | nullable; use for temporary role/employee module or feature visibility |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |
| UNIQUE: `(tenant_id, grantee_type, grantee_id, module, feature_key)` | | |

### `sessions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `user_id` | `uuid` | FK → users |
| `tenant_id` | `uuid` | FK -> tenants |
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

### `employee_hierarchy_closure`

Current position-derived closure table for org hierarchy. Owned by Org Structure and rebuilt from current `position_reporting_history` plus active `position_assignments` when position reporting or occupancy changes. Auth consumes it for current access scope resolution; historical reporting uses `position_assignments` plus `position_reporting_history`.

| Column | Type | Notes |
|:-------|:-----|:------|
| `tenant_id` | `uuid` | FK -> tenants |
| `ancestor_employee_id` | `uuid` | FK -> employees; resolved manager/ancestor employee |
| `descendant_employee_id` | `uuid` | FK -> employees; resolved report/subordinate employee |
| `depth` | `int` | 0 = self-row; 1 = direct report; 2+ = skip-level |
| PK: `(tenant_id, ancestor_employee_id, descendant_employee_id)` | | |

Every employee has a self-row (`depth = 0`). Queries: `depth = 1` for `direct_reports`; `depth >= 1` for `reporting_tree`.

### `audit_logs`

Append-only audit trail. Partitioned by month via `pg_partman`.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `user_id` | `uuid` | FK → users (nullable for system actions) |
| `action` | `varchar(100)` | e.g., `employee.created`, `leave.approved` |
| `resource_type` | `varchar(50)` | e.g., `Employee`, `LeaveRequest` |
| `resource_id` | `uuid` | |
| `old_values_json` | `jsonb` | Previous state |
| `new_values_json` | `jsonb` | New state |
| `ip_address` | `varchar(45)` | |
| `correlation_id` | `uuid` | Request correlation |
| `created_at` | `timestamptz` | |

### `legal_acceptance_records`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `user_id` | `uuid` | FK -> users |
| `document_type` | `varchar(80)` | `terms`, `privacy_notice`, `activity_monitoring_notice`, `screenshot_notice`, `biometric_photo_consent`, `marketing` |
| `document_version` | `varchar(50)` | Version accepted/acknowledged; references the published version string from Developer Platform `legal_document_versions` |
| `decision` | `varchar(20)` | `accepted`, `acknowledged`, `declined` |
| `required` | `boolean` | Whether the item blocks access or collection |
| `decided_at` | `timestamptz` | |
| `ip_address` | `varchar(45)` | |
| `user_agent` | `varchar(500)` | |
| `source` | `varchar(30)` | `invite`, `web`, `desktop-agent` |

Compliance Center manages legal_document_versions; Auth records user decisions in legal_acceptance_records.

## Domain Events (intra-module — MediatR)

> These events are published and consumed within this module only. They never leave the module.

| Event | Published When | Handler |
|:------|:---------------|:--------|
| _(none)_ | — | — |

## Cross-Module Events (cross-module — MediatR INotification)

### Publishes

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `UserLoggedIn` | User successfully authenticates | [[modules/shared-platform/overview\|Shared Platform]] (session tracking) |
| `UserLoggedOut` | User logs out or session expires | [[modules/shared-platform/overview\|Shared Platform]] |
| `RoleAssigned` | Role assigned to a user | Downstream permission consumers |
| `PermissionChanged` | Individual permission override set or removed | Downstream permission consumers |

### Consumes

| Event | Source Module | Action Taken |
|:------|:-------------|:-------------|
| `UserStatusChanged` | [[modules/infrastructure/overview\|Infrastructure]] | Activate or deactivate user login access |

---

## Key Business Rules

1. **Customer web BFF sessions** — HttpOnly session cookies with backend-held tenant auth state/JWT and `perm_ver` for real-time permission staleness checks.
2. **Password hashing** - BCrypt with work factor 12. Do not use any other algorithm for user passwords.
3. **Hybrid permission control** — commercial entitlement decides which modules and feature keys exist for the tenant; runtime flags decide which included features are active; RBAC decides who can use them. Effective permissions = universal auto-grants + active role permissions + valid individual overrides; filtered by subscription/module entitlements, selected feature keys, runtime flags, and optional role/employee feature visibility grants; scoped by org hierarchy.
4. **Permission version counter** — Phase 1 in-memory key `perm_version:{user_id}`. Incremented on any permission/role change. `PermissionVersionMiddleware` rejects JWTs with stale `perm_ver` with 401 -> frontend silently refreshes. Redis is optional/future distributed infrastructure for multi-instance deployments.
5. **Access scope scoping** - employee-data access is resolved from `user_roles.scope_type` and `user_roles.scope_id`, then checked against the target employee, department, team, own-record, or reporting relationship. The frontend never sends employee ID lists. Tenant Super Admin uses `Organization` scope. Non-admin cross-tree exceptions use hierarchy bypass grants (Path C).
6. **Never hardcode role names** — roles are custom, created by Tenant Super Admin or delegated permission admins. Always check permissions, never role names.
7. **Role templates are provisioning blueprints** — Developer Platform templates can seed tenant roles, but tenant owners can later edit/create roles using only permissions exposed by their enabled modules.
8. **Device JWT** for agents — contains `device_id` + `tenant_id` + `type: "agent"` claim. No user permissions.
9. **Refresh token rotation** — each use generates a new token, old one is marked with `replaced_by_id`. If a revoked token is reused, the entire replacement chain is revoked (token theft detection).
10. **MFA** - MFA uses authenticator-app TOTP as the primary method. Login with MFA enabled returns an `mfa_pending` scoped token and verifies a 6-digit authenticator code. Email OTP is fallback/recovery only; fallback OTPs are hashed at rest, expire after 5 minutes, and are single-use.
11. **Forced password change** — Dev Platform admin sets `must_change_password = true` on `users`. On login the server issues a 10-min `change_password` scoped JWT instead of a full web session. The client must call POST `/auth/change-password` before getting a regular session.
12. **Legal & Privacy gates** - Terms and Privacy Notice block account activation/dashboard access; WorkPulse collection-required items block only the affected collector or verification path.
13. **Audit logs are append-only** — partitioned by month, never deleted (compliance requirement).

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| POST | `/api/v1/auth/login` | Public | Login |
| POST | `/api/v1/auth/refresh` | Public | Refresh cookie-backed session |
| POST | `/api/v1/auth/logout` | Authenticated | Logout |
| POST | `/api/v1/auth/mfa/enable` | Authenticated | Begin TOTP MFA setup |
| POST | `/api/v1/auth/mfa/confirm` | Authenticated | Confirm TOTP MFA setup |
| POST | `/api/v1/auth/mfa/send` | `mfa_pending` | Send/resend email OTP fallback challenge |
| POST | `/api/v1/auth/mfa/verify` | `mfa_pending` | Verify TOTP or allowed fallback code |
| GET | `/api/v1/roles` | `roles:read` | List roles |
| POST | `/api/v1/roles` | `roles:manage` | Create role |
| PUT | `/api/v1/roles/{id}` | `roles:manage` | Update role |
| POST | `/api/v1/roles/{id}/permissions` | `roles:manage` | Set role permissions |
| GET | `/api/v1/team-roles` | `roles:manage` | List standard team roles and scoped permission sets |
| PUT | `/api/v1/team-roles/{id}/permissions` | `roles:manage` | Set team-role permissions from team-scoped permission catalog only |
| GET | `/api/v1/permissions/catalog` | `roles:manage` | List assignable permissions filtered by active tenant modules and included/runtime-enabled feature keys |
| GET | `/api/v1/permissions/team-catalog` | `roles:manage` | List assignable team/workspace-scoped permissions for team roles |
| POST | `/api/v1/users/{id}/roles` | `roles:manage` | Assign role to employee |
| GET | `/api/v1/users/{id}/permissions` | `roles:manage` | Get effective permissions |
| POST | `/api/v1/users/{id}/permission-overrides` | `roles:manage` | Grant/revoke permission override |
| DELETE | `/api/v1/users/{id}/permission-overrides/{permId}` | `roles:manage` | Remove override |
| GET | `/api/v1/feature-access` | `roles:manage` | List role/employee feature visibility grants |
| POST | `/api/v1/feature-access` | `roles:manage` | Grant role/employee visibility inside commercial boundary |
| DELETE | `/api/v1/feature-access/{id}` | `roles:manage` | Revoke role/employee visibility grant |
| GET | `/api/v1/audit-logs` | `settings:admin` | Query audit logs |
| GET | `/api/v1/me/app-context` | `employees:read-own` | Session context: capabilities (permission + access policy), navigation items, modules |

## Features

- [[frontend/cross-cutting/authentication|Authentication]] — BFF web sessions, backend-held auth state, refresh/session rotation
- [[frontend/cross-cutting/authorization|Authorization]] — Hybrid permission control: commercial module/feature boundary + runtime flags + roles + per-employee overrides + hierarchy scoping
- [[modules/auth/session-management/overview|Session Management]] — Session tracking, revocation, expiry
- [[modules/auth/mfa/overview|MFA]] — Multi-factor authentication (TOTP primary, email OTP fallback)
- [[modules/auth/audit-logging/overview|Audit Logging]] — Append-only audit trail, partitioned by month
- [[Userflow/Auth-Access/gdpr-consent|Legal & Privacy Acceptance]] - Terms, privacy, monitoring notices, and consent tracking

---

## Related

- [[security/auth-architecture|Auth Architecture]] — BFF web session design, backend-held tenant JWT, device JWT, token rotation
- [[developer-platform/modules/role-template-manager/overview|Role Template Manager]] — Developer Platform starter role templates
- [[infrastructure/multi-tenancy|Multi Tenancy]] — All roles and sessions are tenant-scoped
- [[security/compliance|Compliance]] — Audit logs are never deleted; Legal & Privacy acceptance records
- [[security/data-classification|Data Classification]] — Refresh tokens hashed (SHA-256), never stored raw
- [[backend/shared-kernel|Shared Kernel]] — `ICurrentUser`, `RequirePermissionAttribute` used by all modules
- [[code-standards/logging-standards|Logging Standards]] — Correlation IDs in audit logs
- [[current-focus/DEV2-auth-security|DEV2: Auth Security]] — Implementation task file

See also: [[backend/module-catalog|Module Catalog]], [[modules/infrastructure/overview|Infrastructure]], [[security/auth-architecture|Auth Architecture]], [[security/compliance|Compliance]]
