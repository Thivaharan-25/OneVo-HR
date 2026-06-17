# Auth & Security — Schema

**Module:** [[modules/auth/overview|Auth & Security]]
**Phase:** Phase 1
**Tables:** 16

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
| `module` | `varchar(50)` | Module key, e.g. `core_hr`, `leave`, `work_management` |
| `feature_key` | `varchar(120)` | Optional feature key inside the module, e.g. `leave.requests` |
| `is_enabled` | `boolean` |  |
| `granted_by` | `uuid` | FK → users |
| `valid_from` | `timestamptz` | Nullable; defaults to active immediately |
| `expires_at` | `timestamptz` | Nullable; use for temporary role/employee module or feature visibility |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |
| UNIQUE: `(tenant_id, grantee_type, grantee_id, module, feature_key)` | | |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `granted_by` → [[database/schemas/infrastructure#`users`|users]]

> **Polymorphic FK — enforced at application layer:** when `grantee_type = 'role'`, `grantee_id` references [[#`roles`|roles]]; when `grantee_type = 'employee'`, `grantee_id` references [[database/schemas/infrastructure#`users`|users]]. No DB-level FK constraint on `grantee_id`.

This table is not a billing or subscription table. It can only narrow or expose role/employee visibility inside a module/feature that is already commercially included for the tenant.

---

## `legal_acceptance_records`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `user_id` | `uuid` | FK → users |
| `document_type` | `varchar(80)` | `terms`, `privacy_notice`, `activity_monitoring_notice`, `screenshot_notice`, `biometric_photo_consent`, `marketing` |
| `document_version` | `varchar(50)` | Version accepted/acknowledged; references the published version string from Developer Platform `legal_document_versions` |
| `decision` | `varchar(20)` | `accepted`, `acknowledged`, `declined` |
| `required` | `boolean` | Whether the item blocks platform access or affected collection |
| `decided_at` | `timestamptz` |  |
| `ip_address` | `varchar(45)` |  |
| `user_agent` | `varchar(500)` |  |
| `source` | `varchar(30)` | `invite`, `web`, `desktop-agent` |

Compliance Center manages published legal document versions in legal_document_versions. Auth records each user's acceptance, acknowledgement, or decline decision in legal_acceptance_records.

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

## `invitation_tokens`

Secure one-time invitation records for tenant owner/admin invites and normal user invites. Raw invite tokens are never stored; only a SHA-256 hash is persisted.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `user_id` | `uuid` | FK -> users; pending invited account |
| `role_id` | `uuid` | Nullable FK → roles; role to assign on acceptance; required for provisioning owner invites |
| `invited_email` | `varchar(255)` | Original email address the invite was sent to |
| `invited_full_name` | `varchar(255)` | Display name of invitee; used in invite email and accept flow |
| `token_hash` | `varchar(128)` | SHA-256 hash of invite token; never store raw token |
| `status` | `varchar(20)` | `pending`, `accepted`, `expired`, `revoked` |
| `completion_methods_json` | `jsonb` | Allowed methods: `password`, `google` |
| `completed_with` | `varchar(20)` | Nullable; `password` or `google` |
| `allow_google_email_mismatch` | `boolean` | Whether Google email may differ from invited email |
| `allowed_email_domains_json` | `jsonb` | Allowed domains for Google email mismatch |
| `expires_at` | `timestamptz` | Usually 72 hours after creation |
| `used_at` | `timestamptz` | Nullable; set when invite is completed |
| `revoked_at` | `timestamptz` | Nullable |
| `revoked_by_id` | `uuid` | Nullable FK -> users or dev platform account boundary |
| `created_by_id` | `uuid` | FK -> users or dev platform account boundary |
| `created_at` | `timestamptz` | |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `user_id` -> [[database/schemas/infrastructure#`users`|users]]

**Rules:** completing with password uses `invited_email`. Completing with Google may use a different verified Google email only when `allow_google_email_mismatch = true` and the domain is allowed. Mismatches are audit-logged and the original `invited_email` remains on this record.

---

## `tenant_auth_policies`

Tenant-level defaults for login and invitation completion methods.

| Column | Type | Notes |
|:-------|:-----|:------|
| `tenant_id` | `uuid` | PK, FK -> tenants |
| `password_login_enabled` | `boolean` | Whether password login is allowed |
| `google_login_enabled` | `boolean` | Whether Google login/invite completion is allowed |
| `invite_google_email_mismatch_allowed` | `boolean` | Default mismatch rule for invitations |
| `allowed_login_domains_json` | `jsonb` | Allowed email domains for SSO/Google mismatch |
| `mfa_required` | `boolean` | Tenant-wide MFA requirement |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | Nullable |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `user_external_identities`

External identity links for tenant users. Use this instead of overloading `users.email` for provider identity details.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `user_id` | `uuid` | FK -> users |
| `provider` | `varchar(30)` | `google`; future providers may include SAML/OIDC |
| `provider_subject` | `varchar(255)` | Stable provider subject, e.g., Google `sub` |
| `provider_email` | `varchar(255)` | Verified email returned by provider |
| `email_verified` | `boolean` | Provider email verification state |
| `linked_at` | `timestamptz` | |
| `last_used_at` | `timestamptz` | Nullable |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `user_id` -> [[database/schemas/infrastructure#`users`|users]]

**Unique:** `(tenant_id, provider, provider_subject)`, `(tenant_id, provider, user_id)`

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
| `source_template_id` | `uuid` | Nullable FK -> role_templates when materialized from a reusable template |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]]

---

**Rule:** roles do not require job levels. They are tenant-scoped permission containers. Job levels, reporting lines, and hierarchy can suggest or scope access decisions, workflows, escalation, and organisation-aware policies, but job levels must not auto-assign permissions.

## `role_templates`

Developer Platform starter role definitions. Templates are global/operator-managed and are materialized into tenant-scoped `roles` only after validation against the tenant's enabled modules.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `name` | `varchar(100)` | e.g., `Tenant Owner`, `HR Admin`, `Leave Manager` |
| `description` | `varchar(255)` | Nullable |
| `module_keys_json` | `jsonb` | Modules this template is intended for |
| `permission_codes_json` | `jsonb` | Permission codes included in the template |
| `is_system` | `boolean` | ONEVO default template |
| `version` | `integer` | Template version |
| `is_active` | `boolean` | |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | Nullable |

**Rule:** applying a template to a tenant must filter/validate permissions through the tenant module entitlement catalog. Permissions for disabled, available, quoted, unpurchased, or expired modules must not be granted. Operators may also create tenant-specific roles during provisioning without saving them as reusable templates.

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
| `scope_type` | `varchar(30)` | Nullable. `Organization`, `Department`, `DepartmentTree`, `Team`, `Own`, `DirectReports`, or `ReportingTree` |
| `scope_id` | `uuid` | Nullable. Department/team id when scope needs a boundary; null for `Organization`, `Own`, `DirectReports`, and `ReportingTree` |
| `reason` | `varchar(255)` | Why this override exists |
| `valid_from` | `timestamptz` | Nullable |
| `expires_at` | `timestamptz` | Nullable |
| `granted_by` | `uuid` | FK → users (Super Admin who set this) |
| `created_at` | `timestamptz` |  |
| UNIQUE: `(tenant_id, user_id, permission_id)` | | |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `user_id` → [[database/schemas/infrastructure#`users`|users]], `permission_id` → [[#`permissions`|permissions]], `granted_by` → [[database/schemas/infrastructure#`users`|users]]

**Scope rule:** Scoped overrides may narrow or explicitly grant an employee-data permission at a boundary. If `scope_type` is `Department`, `DepartmentTree`, or `Team`, `scope_id` is required. If `scope_type` is `Organization`, `Own`, `DirectReports`, or `ReportingTree`, `scope_id` must be null.

---

## `user_roles`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `user_id` | `uuid` | FK -> users |
| `role_id` | `uuid` | FK -> roles |
| `scope_type` | `varchar(30)` | `Organization`, `Department`, `DepartmentTree`, `Team`, `Own`, `DirectReports`, or `ReportingTree` |
| `scope_id` | `uuid` | Nullable. Department/team id when scope needs a boundary; null for `Organization`, `Own`, `DirectReports`, and `ReportingTree` |
| `source_type` | `varchar(30)` | `Manual`, `PositionTemplate`, or `EmployeeOverride` |
| `source_position_id` | `uuid` | Nullable FK -> positions when generated from a position |
| `source_position_access_template_id` | `uuid` | Nullable FK -> position_access_templates |
| `effective_from` | `timestamptz` | Nullable; defaults to immediate when null |
| `effective_to` | `timestamptz` | Nullable |
| `status` | `varchar(20)` | `Active`, `Scheduled`, `PendingApproval`, `Expired`, or `Revoked` |
| `assigned_at` | `timestamptz` |  |
| `assigned_by` | `uuid` | FK -> users (who granted this) |
| `approved_by` | `uuid` | Nullable FK -> users |
| `expires_at` | `timestamptz` | Deprecated compatibility alias; use `effective_to` for time-bound role grants |
| UNIQUE: `(tenant_id, user_id, role_id, scope_type, scope_id)` | | Must use `NULLS NOT DISTINCT` or an equivalent normalized/partial unique index so null `scope_id` values cannot create duplicate grants |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `user_id` -> [[database/schemas/infrastructure#`users`|users]], `role_id` -> [[#`roles`|roles]], `assigned_by` -> [[database/schemas/infrastructure#`users`|users]], `approved_by` -> [[database/schemas/infrastructure#`users`|users]], `source_position_id` -> [[database/schemas/org-structure#`positions`|positions]], `source_position_access_template_id` -> [[database/schemas/org-structure#`position_access_templates`|position_access_templates]]

**Source rule:** Position access templates generate real `user_roles` rows. The generated row is the active grant after confirmation or approval; the position template itself is never treated as an active permission grant.

---

## `access_grant_requests`

Approval records for sensitive position-template access generated during onboarding, transfer, promotion, or position assignment when the actor does not have `roles:manage` or `access:approve`.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `user_id` | `uuid` | FK -> users who will receive the grant |
| `action_type` | `varchar(30)` | `Onboarding`, `Transfer`, `Promotion`, or `PositionAssignment` |
| `target_position_id` | `uuid` | FK -> positions |
| `target_department_id` | `uuid` | FK -> departments; used for approver routing |
| `position_access_template_id` | `uuid` | FK -> position_access_templates |
| `requested_role_id` | `uuid` | FK -> roles |
| `requested_scope_type` | `varchar(30)` | Requested grant scope |
| `requested_scope_id` | `uuid` | Nullable requested grant boundary |
| `approval_status` | `varchar(20)` | `Pending`, `Approved`, `Rejected`, or `Cancelled` |
| `requested_by` | `uuid` | FK -> users |
| `approved_by` | `uuid` | Nullable FK -> users |
| `requested_at` | `timestamptz` |  |
| `decided_at` | `timestamptz` | Nullable |
| `effective_from` | `timestamptz` | Grant effective start after approval |
| `effective_to` | `timestamptz` | Nullable grant end |
| `decision_comment` | `varchar(500)` | Nullable |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` -> [[database/schemas/core-hr#`employees`|employees]], `user_id` -> [[database/schemas/infrastructure#`users`|users]], `target_position_id` -> [[database/schemas/org-structure#`positions`|positions]], `target_department_id` -> [[database/schemas/org-structure#`departments`|departments]], `position_access_template_id` -> [[database/schemas/org-structure#`position_access_templates`|position_access_templates]], `requested_role_id` -> [[#`roles`|roles]], `requested_by` -> [[database/schemas/infrastructure#`users`|users]], `approved_by` -> [[database/schemas/infrastructure#`users`|users]]

**Routing rule:** Approver resolution uses `target_department_id`: first users with `roles:manage` or `access:approve` whose own scope covers the target department, then tenant-wide users with that authority, then Tenant Admin. If multiple approvers match, all are notified and the first approval wins.

**Scope rule:** Scope belongs to the role assignment or scoped override, not the permission. The same security role can be assigned to different users at `Organization`, `Department`, `DepartmentTree`, `Team`, `Own`, `DirectReports`, or `ReportingTree` scope.

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

Multi-factor authentication method registrations per user. MFA uses `totp` as the primary method. `email_otp_fallback` is fallback/recovery only when policy permits it.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `user_id` | `uuid` | FK → users |
| `tenant_id` | `uuid` | FK → tenants |
| `method` | `varchar(20)` | `totp`, `email_otp_fallback` |
| `secret_encrypted` | `varchar(500)` | Encrypted TOTP secret for `totp`; temporary hashed fallback OTP only for `email_otp_fallback` challenges |
| `is_verified` | `boolean` | User has confirmed setup with a valid code |
| `last_used_at` | `timestamptz` | Nullable |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` | Nullable |
| UNIQUE: `(user_id, method)` | | One row per method per user |

**Foreign Keys:** `user_id` → [[database/schemas/infrastructure#`users`|users]], `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `mfa_recovery_codes`

One-time-use backup codes generated when MFA is first enabled. Stored as BCrypt hashes, never plaintext. Each code is consumed on use.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `user_id` | `uuid` | FK → users |
| `code_hash` | `varchar(255)` | BCrypt hash of the recovery code |
| `used_at` | `timestamptz` | Nullable — set when the code is consumed |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `user_id` → [[database/schemas/infrastructure#`users`|users]]

---

## Related

- [[modules/auth/overview|Auth & Security Module]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]
