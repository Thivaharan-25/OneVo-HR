# Auth & Security — Schema

**Module:** [[modules/auth/overview|Auth & Security]]
**Phase:** Phase 1
**Tables:** 12

---

## `audit_logs`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `user_id` | `uuid` | FK → users (nullable for system actions) |
| `action` | `varchar(100)` | e.g., `employee.created`, `leave.approved` |
| `resource_type` | `varchar(50)` | e.g., `Employee`, `LeaveRequest` |
| `resource_id` | `uuid` |  |
| `old_values_json` | `jsonb` | Previous state |
| `new_values_json` | `jsonb` | New state |
| `ip_address` | `varchar(45)` |  |
| `correlation_id` | `uuid` | Request correlation |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `user_id` → [[database/schemas/infrastructure#`users`|users]]

---

## `feature_access_grants`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `grantee_type` | `varchar(10)` | `role` or `employee` |
| `grantee_id` | `uuid` | FK → roles.id OR users.id (polymorphic, depends on grantee_type) |
| `module` | `varchar(50)` | Module code: `leave`, `payroll`, `performance`, etc. |
| `is_enabled` | `boolean` |  |
| `granted_by` | `uuid` | FK → users |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |
| UNIQUE: `(tenant_id, grantee_type, grantee_id, module)` | | |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `granted_by` → [[database/schemas/infrastructure#`users`|users]]

> **Polymorphic FK — enforced at application layer:** when `grantee_type = 'role'`, `grantee_id` references [[#`roles`|roles]]; when `grantee_type = 'employee'`, `grantee_id` references [[database/schemas/infrastructure#`users`|users]]. No DB-level FK constraint on `grantee_id`.

---

## `gdpr_consent_records`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `user_id` | `uuid` | FK → users |
| `consent_type` | `varchar(50)` | `data_processing`, `biometric`, `monitoring`, `marketing` |
| `consented` | `boolean` |  |
| `consented_at` | `timestamptz` |  |
| `ip_address` | `varchar(45)` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `user_id` → [[database/schemas/infrastructure#`users`|users]]

---

## `permissions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `code` | `varchar(50)` | e.g., `employees:read`, `workforce:view`, `exceptions:manage` |
| `description` | `varchar(255)` |  |
| `module` | `varchar(50)` | Which module this permission belongs to |

---

## `role_permissions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `role_id` | `uuid` | FK → roles |
| `permission_id` | `uuid` | FK → permissions |
| PK: `(role_id, permission_id)` | | |

**Foreign Keys:** `role_id` → [[#`roles`|roles]], `permission_id` → [[#`permissions`|permissions]]

---

## `roles`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(50)` | e.g., "HR Manager", "CEO", "Employee" |
| `description` | `varchar(255)` |  |
| `is_system` | `boolean` | System roles can't be deleted |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `sessions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `user_id` | `uuid` | FK → users |
| `tenant_id` | `uuid` | FK → tenants |
| `ip_address` | `varchar(45)` |  |
| `user_agent` | `varchar(500)` |  |
| `started_at` | `timestamptz` |  |
| `last_activity_at` | `timestamptz` |  |
| `expires_at` | `timestamptz` |  |
| `is_revoked` | `boolean` |  |

**Foreign Keys:** `user_id` → [[database/schemas/infrastructure#`users`|users]], `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `user_permission_overrides`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `user_id` | `uuid` | FK → users |
| `permission_id` | `uuid` | FK → permissions |
| `grant_type` | `varchar(10)` | `grant` or `revoke` |
| `reason` | `varchar(255)` | Why this override exists |
| `granted_by` | `uuid` | FK → users (Super Admin who set this) |
| `created_at` | `timestamptz` |  |
| UNIQUE: `(tenant_id, user_id, permission_id)` | | |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `user_id` → [[database/schemas/infrastructure#`users`|users]], `permission_id` → [[#`permissions`|permissions]], `granted_by` → [[database/schemas/infrastructure#`users`|users]]

---

## `user_roles`

| Column | Type | Notes |
|:-------|:-----|:------|
| `user_id` | `uuid` | FK → users |
| `role_id` | `uuid` | FK → roles |
| `assigned_at` | `timestamptz` |  |
| `assigned_by` | `uuid` | FK → users (who granted this) |
| `expires_at` | `timestamptz` | Nullable — set for time-bound role grants |
| PK: `(user_id, role_id)` | | |

**Foreign Keys:** `user_id` → [[database/schemas/infrastructure#`users`|users]], `role_id` → [[#`roles`|roles]], `assigned_by` → [[database/schemas/infrastructure#`users`|users]]

---

## `refresh_tokens`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `user_id` | `uuid` | FK → users |
| `token_hash` | `varchar(128)` | SHA-256 hash of token — never store raw |
| `expires_at` | `timestamptz` | 7 days from creation |
| `replaced_by_id` | `uuid` | Self-referencing FK — token rotation chain |
| `revoked_at` | `timestamptz` | Nullable — set when token is revoked |
| `created_at` | `timestamptz` | |

**Foreign Keys:** `user_id` → [[database/schemas/infrastructure#`users`|users]], `replaced_by_id` → [[#`refresh_tokens`|refresh_tokens]]

---

## `user_mfa`

Multi-factor authentication method registrations per user. Each row is one verified MFA method (e.g. `totp`). Unverified setups are stored temporarily until `is_verified = true`.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `user_id` | `uuid` | FK → users |
| `tenant_id` | `uuid` | FK → tenants |
| `method` | `varchar(20)` | `totp` or `email_otp` |
| `secret_encrypted` | `varchar(500)` | Encrypted TOTP secret (base32) or email address |
| `is_verified` | `boolean` | User has confirmed setup with a valid code |
| `last_used_at` | `timestamptz` | Nullable |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` | Nullable |
| UNIQUE: `(user_id, method)` | | One row per method per user |

**Foreign Keys:** `user_id` → [[database/schemas/infrastructure#`users`|users]], `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `mfa_recovery_codes`

One-time-use backup codes generated when MFA is first enabled. Stored as SHA-256 hashes, never plaintext. Each code is consumed on use.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `user_id` | `uuid` | FK → users |
| `code_hash` | `varchar(128)` | SHA-256 hex hash of the recovery code |
| `used_at` | `timestamptz` | Nullable — set when the code is consumed |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `user_id` → [[database/schemas/infrastructure#`users`|users]]

---

## Related

- [[modules/auth/overview|Auth & Security Module]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]