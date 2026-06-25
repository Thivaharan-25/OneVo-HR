# Developer Platform Database Schema

## Overview

The OneVo Developer Platform introduces dedicated tables to manage platform users, platform roles and permissions, authentication sessions, and platform auth events in Phase 1. Phase 2 adds agent version releases, deployment ring assignments, and platform API keys. This schema enables:

- **Multi-tenant admin isolation**: Developer Platform users operate independently from tenant-facing systems
- **Permission-based platform RBAC**: Platform roles restrict access to Developer Platform modules and `/admin/v1/*` actions
- **Agent release management**: Phase 2 semantic versioning, release channels (stable/beta/recalled), and OS compatibility tracking
- **Gradual rollout capabilities**: Phase 2 deployment rings (Internal, Beta, GA) allow controlled agent version distribution across tenants
- **Session security**: Email/password plus mandatory MFA before session creation, with token management and IP tracking
- **API access control**: Platform API key provisioning with scope-based permissions and expiration

**Phase 1** adds platform user/session/RBAC/auth-event tables plus the `global_app_catalog` table in the SharedPlatform schema managed by the App Catalog module. **Phase 2** adds release/ring management tables and the `platform_api_keys` table for programmatic access.

---

## DbContext Ownership (ADR-001)

> **DbContext:** `ApplicationDbContext` in `ONEVO.Infrastructure/Persistence/`. Phase 1 DevPlatform entities (`PlatformUser`, `PlatformUserSession`, `PlatformRole`) are configured in `ONEVO.Infrastructure/Persistence/Configurations/DevPlatform/`. Phase 2 adds `AgentVersionRelease`, `AgentDeploymentRing`, and `AgentDeploymentRingAssignment`. These entities have **no TenantId** and are excluded from the global tenant query filter.

Per [ADR-001](../../decisions/ADR-001-per-module-database-and-event-bus.md), all developer platform tables are mapped by the unified `ApplicationDbContext`. EF migrations live in `ONEVO.Infrastructure/Persistence/Migrations/` and are run as part of the standard application startup.

Cross-module data access (e.g., reading `tenants`) goes through the existing module's public service interface via DI - never by querying the DbContext directly across module boundaries.

---

## Schema Catalog Impact

| Phase | Change | Table Count |
|-------|--------|------------|
| Current | Baseline | 170 |
| Phase 1 | DevPlatform user/session/RBAC/auth-event tables + `global_app_catalog` (SharedPlatform) + `observed_applications` (Configuration) + 3 columns on `app_allowlists` | Finalized by Phase 1 migration cut |
| Phase 2 | Agent release/ring management tables + `platform_api_keys` | Finalized by Phase 2 migration cut |

> **Note on ownership:** `global_app_catalog` is owned by `SharedPlatformDbContext` and `observed_applications` by `ConfigurationDbContext`. They are not in `ApplicationDbContext`. The dev console manages them through `IGlobalAppCatalogService` and `IObservedApplicationReader` interfaces respectively.

---

## Phase 1 Tables

### platform_users

Administrative users for the Developer Platform. Email/password plus MFA is the primary login journey. Optional Google OAuth can be linked for invited platform managers where policy allows, but it never bypasses MFA. Effective access is permission-based through user-role and role-permission mappings.

| Column | Type | Constraints / Notes |
|--------|------|-------------------|
| id | uuid | PRIMARY KEY |
| email | varchar(255) | UNIQUE, NOT NULL |
| full_name | varchar(255) | NOT NULL |
| google_sub | varchar(255) | Nullable Google OAuth subject identifier for optional invited-manager OAuth setup/sign-in |
| status | varchar(20) | `pending`, `active`, or `inactive` |
| mfa_status | varchar(20) | `not_enrolled`, `enrolled`, `locked`, or equivalent policy state |
| invite_status | varchar(20) | `pending`, `accepted`, `revoked`, `expired` |
| created_by_id | uuid | FK -> platform_users(id), nullable for seed Super Admin |
| created_at | timestamptz | NOT NULL; creation timestamp |
| last_login_at | timestamptz | Nullable; tracks last successful authentication |

**Indexes**: `UNIQUE(email)`, `btree(status)`, `btree(invite_status)`

---

### platform_user_invites

Pending invitations for platform managers.

| Column | Type | Constraints / Notes |
|--------|------|-------------------|
| id | uuid | PRIMARY KEY |
| email | varchar(255) | NOT NULL |
| full_name | varchar(255) | NOT NULL |
| invite_token_hash | varchar(64) | NOT NULL; raw token never stored |
| invited_by_id | uuid | FOREIGN KEY -> platform_users(id), NOT NULL |
| expires_at | timestamptz | NOT NULL |
| accepted_at | timestamptz | Nullable |
| revoked_at | timestamptz | Nullable |
| created_at | timestamptz | NOT NULL |

---

### platform_roles

Platform role presets and custom roles.

| Column | Type | Constraints / Notes |
|--------|------|-------------------|
| id | uuid | PRIMARY KEY |
| name | varchar(100) | NOT NULL |
| description | text | Nullable |
| is_system | boolean | System roles can be cloned but not deleted |
| is_active | boolean | Default true |
| created_by_id | uuid | FOREIGN KEY -> platform_users(id), nullable for seed roles |
| created_at | timestamptz | NOT NULL |
| updated_at | timestamptz | NOT NULL |

---

### platform_permissions

Catalog of platform-admin permissions. These control Developer Platform modules only; they are not tenant permissions.

| Column | Type | Constraints / Notes |
|--------|------|-------------------|
| code | varchar(120) | PRIMARY KEY, e.g. `platform.tenants.read` |
| module_key | varchar(80) | Developer Platform module key |
| description | text | Nullable |
| is_high_risk | boolean | Marks permissions such as impersonation and account management |

---

### platform_role_permissions

Maps platform roles to platform permissions.

| Column | Type | Constraints / Notes |
|--------|------|-------------------|
| role_id | uuid | FOREIGN KEY -> platform_roles(id), NOT NULL |
| permission_code | varchar(120) | FOREIGN KEY -> platform_permissions(code), NOT NULL |
| granted_by_id | uuid | FOREIGN KEY -> platform_users(id), NOT NULL |
| granted_at | timestamptz | NOT NULL |

**Primary key:** `(role_id, permission_code)`

---

### platform_user_roles

Maps platform users to platform roles.

| Column | Type | Constraints / Notes |
|--------|------|-------------------|
| user_id | uuid | FOREIGN KEY -> platform_users(id), NOT NULL |
| role_id | uuid | FOREIGN KEY -> platform_roles(id), NOT NULL |
| assigned_by_id | uuid | FOREIGN KEY -> platform_users(id), NOT NULL |
| assigned_at | timestamptz | NOT NULL |

**Primary key:** `(user_id, role_id)`

---

### platform_user_sessions

Authenticated sessions for Developer Platform users. A session is created only after MFA succeeds.

| Column | Type | Constraints / Notes |
|--------|------|-------------------|
| id | uuid | PRIMARY KEY |
| account_id | uuid | FOREIGN KEY -> platform_users(id), NOT NULL |
| token_hash | varchar(64) | SHA256 hash of session token, NOT NULL |
| created_at | timestamptz | NOT NULL |
| expires_at | timestamptz | NOT NULL; session TTL |
| ip_address | varchar(45) | Nullable; IPv4 or IPv6, for audit/security |

**Indexes**: `btree(user_id)`, `btree(expires_at)`

**Notes**: Tokens are hashed; original token never stored. Expired sessions are soft-deleted or archived for audit.

---

### platform_auth_events

Immutable authentication and access history for Developer Platform users.

| Column | Type | Constraints / Notes |
|--------|------|-------------------|
| id | uuid | PRIMARY KEY |
| user_id | uuid | Nullable FK -> platform_users(id); nullable for failed login before user resolution |
| event_type | varchar(80) | Examples: `login_succeeded`, `login_failed`, `mfa_succeeded`, `mfa_failed`, `password_reset_requested`, `password_reset_completed`, `session_revoked` |
| source_ip | varchar(45) | Nullable |
| user_agent | text | Nullable |
| metadata_json | jsonb | Safe structured context only; no passwords, tokens, or secrets |
| created_at | timestamptz | NOT NULL |

---

## Phase 2 Tables

### agent_version_releases

Agent binary releases with version metadata, channels, and OS requirements.

| Column | Type | Constraints / Notes |
|--------|------|-------------------|
| id | uuid | PRIMARY KEY |
| version | varchar(20) | NOT NULL; semver format (e.g., `'1.4.2'`) |
| release_channel | varchar(20) | NOT NULL; enum: `'stable'` \| `'beta'` \| `'recalled'` |
| min_os_version | varchar(20) | Nullable; minimum OS version required (e.g., `'10.0.26000'` for Windows) |
| release_notes | text | Nullable; markdown-formatted changelog |
| download_url | varchar(500) | NOT NULL; CDN or S3 URL to agent binary |
| published_by_id | uuid | FOREIGN KEY -> platform_users(id), NOT NULL |
| published_at | timestamptz | NOT NULL; release publication time |
| recalled_at | timestamptz | Nullable; if set, version is marked as recalled/unsafe |

**Indexes**: `btree(version, release_channel)`, `btree(release_channel)`, `btree(published_at DESC)`

**Notes**: Recalled releases remain in schema for audit but are excluded from deployment eligibility queries.

---

### agent_deployment_rings

Deployment rings for phased agent rollouts. Defines the rollout strategy tiers.

| Column | Type | Constraints / Notes |
|--------|------|-------------------|
| id | uuid | PRIMARY KEY |
| ring_number | int | NOT NULL; enum: `0` (Internal) \| `1` (Beta) \| `2` (GA) |
| name | varchar(50) | NOT NULL; human-readable ring name (`'Internal'` \| `'Beta'` \| `'GA'`) |
| description | text | Nullable; explains ring purpose and rollout scope |

**Indexes**: `UNIQUE(ring_number)`, `btree(name)`

**Notes**: Immutable reference data. Three rings provide a standard phased rollout pattern.

---

### agent_deployment_ring_assignments

Maps tenants to deployment rings, controlling which agent versions they receive.

| Column | Type | Constraints / Notes |
|--------|------|-------------------|
| id | uuid | PRIMARY KEY |
| tenant_id | uuid | FOREIGN KEY -> tenants(id), NOT NULL |
| ring_id | uuid | FOREIGN KEY -> agent_deployment_rings(id), NOT NULL |
| assigned_by_id | uuid | FOREIGN KEY -> platform_users(id), NOT NULL |
| assigned_at | timestamptz | NOT NULL; assignment timestamp for audit |

**Indexes**: `UNIQUE(tenant_id, ring_id)`, `btree(ring_id)`, `btree(assigned_by_id)`

**Notes**: A tenant can belong to only one ring at a time (enforced by unique constraint). Ensures consistent version delivery within a ring cohort.

---

### platform_api_keys

API keys for programmatic access to the developer platform admin API. Supports revocation and expiration.

| Column | Type | Constraints / Notes |
|--------|------|-------------------|
| id | uuid | PRIMARY KEY |
| key_hash | varchar(64) | SHA256 hash of the API key, NOT NULL, UNIQUE |
| name | varchar(100) | NOT NULL; human-readable label for key management |
| scopes | text[] | Array of permission scopes; e.g., `ARRAY['agent:view-health', 'deployment:write']` |
| created_by_id | uuid | FOREIGN KEY -> platform_users(id), NOT NULL |
| expires_at | timestamptz | Nullable; if set, key becomes invalid after this time |
| revoked_at | timestamptz | Nullable; if set, key is revoked and unusable |
| created_at | timestamptz | NOT NULL; key creation time |

**Indexes**: `UNIQUE(key_hash)`, `btree(created_by_id)`, `btree(expires_at)`, `btree(revoked_at)`

**Notes**: Keys are hashed on storage; original key is shown only once at creation. Revoked and expired keys are excluded from validation queries.

---

## Existing Table Changes

### tenants.status Enum

The canonical `tenants.status` lifecycle enum is: `provisioning`, `trial`, `trial_expired`, `pending_payment`, `active`, `suspended`, and `cancelled`. The Developer Platform supports both operator-created provisioning drafts and demo/trial tenants created from Demo Profiles. Detailed wizard progress is stored in `tenant_provisioning_states` and `tenant_provisioning_validation_results`; demo/trial limits and upgrade options are resolved from `demo_profiles`.

| Status | Meaning | Visibility |
|--------|---------|------------|
| `provisioning` | Onboarding draft in progress | Excluded from tenant-facing queries; visible only in admin API for platform managers |
| `trial` | Demo/trial tenant with active trial window and demo profile limits | Limited tenant-facing demo access |
| `trial_expired` | Demo/trial tenant whose trial has expired or was expired by Super Admin | Tenant-facing access blocked except upgrade/support flows where policy allows |
| `pending_payment` | First invoice generated from self-service demo upgrade or operator provisioning and awaiting gateway payment | Limited billing/payment access |
| `active` | Production-ready tenant | Visible in all tenant-facing and admin queries |
| `suspended` | Temporarily disabled | Excluded from tenant-facing queries; visible only in admin API |
| `cancelled` | Commercially cancelled/offboarded tenant | Excluded from tenant-facing queries; visible in admin API for retention, export, and audit workflows |

**Visibility Rule**: Tenants in `provisioning`, `trial_expired`, `suspended`, or `cancelled` status are excluded from:
- Tenant-facing application queries
- Tenant-facing login/session creation
- Standard analytics and reporting

Trial tenants are visible to tenant-facing demo flows while their trial is active and must be limited by the applied Demo Profile. Provisioning, expired, suspended, and cancelled tenants remain visible to developer platform accounts with the required tenant permissions via `/admin/v1/*`.

---

## Provisioning Activation Guard

`PATCH /admin/v1/tenants/{id}/provision/confirm` may activate a tenant only after the provisioning draft is complete. The guard requires:

- Completed tenant profile: company name, slug, primary contact email, country, industry profile, registration/profile name, registration number, estimated employee count, timezone, and currency.
- Persistence rule for tenant profile: country, registration/profile name, registration number, estimated employee count, timezone, currency, and contact metadata are stored as tenant profile/draft state. Tenant provisioning does not create deprecated registration-profile rows. Activation/setup seeding creates the primary legal entity.
- Completed subscription/commercial terms: selected plan, billing cycle/currency, confirmed employee count/company-size bracket, selected optional module add-ons, selected resource-only add-ons, resolved payment gateway config, first-invoice state, shared storage limit, and shared AI token allowance.
- Completed module selection: active modules and each module's sales state are recorded through the entitlement registry.
- Completed role template application: at least the tenant owner/admin starter role is materialized from the module-filtered permission catalog. Role template completion is part of provisioning state, not optional decoration.
- Completed required settings/templates/setup services: monitoring defaults, privacy/transparency mode, Time Off defaults, template applications, setup-service state, and any module-required settings.
- Owner invite state is tracked separately. The invite email is sent only by the explicit invite action, not automatically by tenant creation, configuration, or activation. The same email can be invited to multiple isolated tenants.

Activation fails with `422 Unprocessable Entity` and a checklist of missing steps when any required item is incomplete. Provisioning tenants remain invisible to tenant-facing `/api/v1/*` APIs until activation succeeds.

---

## Security & Access Control

- **Platform Auth Integration**: platform_users authenticate with email/password plus mandatory MFA; optional Google OAuth identifiers can be linked for invited-manager setup/sign-in where enabled. Session tokens are hashed in platform_user_sessions.
- **Permission-Based Access**: Platform roles map to explicit `platform_permissions`; legacy role names are presets only
- **API Key Hashing**: platform_api_keys stores SHA256 hashes; plaintext keys never persisted
- **Audit Trail**: All admin actions (published_by_id, assigned_by_id, created_by_id) track who made changes
- **Tenant Isolation**: dev_platform_* tables are isolated from tenant_facing_* schema; cross-tenant queries are forbidden

---

## Cross-Module Tables Referenced by Developer Platform

The Developer Platform reads and writes many tables owned by existing ONEVO product modules via their service interfaces (never via direct DbContext cross-module access). These tables are defined in their owning module's schema but are documented here for completeness because the Developer Platform's admin API layer depends on them heavily.

**Source of truth:** `database/schema-catalog.md` for all ~294 tables. The canonical table definitions live in `database/schemas/` (one file per module). This section documents the shape of each table as the Developer Platform expects it.

---

### tenants (owned by: SharedPlatform)

Central tenant registry. One row per company onboarded to ONEVO.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `tenant_code` | varchar(30) | UNIQUE, NOT NULL - format `TEN-YYYYMMDD-XXXX` |
| `company_name` | varchar(100) | NOT NULL |
| `legal_company_name` | varchar(150) | NOT NULL |
| `domain` | varchar(255) | UNIQUE, NOT NULL - primary domain |
| `industry` | varchar(80) | NOT NULL |
| `estimated_employee_count` | int | Nullable operator-entered estimate; not final invoice quantity |
| `description` | text | Nullable |
| `phone_number` | varchar(30) | Nullable, E.164 format |
| `website` | varchar(500) | Nullable |
| `country` | varchar(2) | ISO 3166-1 alpha-2, NOT NULL |
| `primary_timezone` | varchar(60) | IANA timezone, NOT NULL |
| `reporting_currency` | varchar(3) | ISO 4217, NOT NULL |
| `date_format` | varchar(20) | e.g. `'DD/MM/YYYY'` |
| `work_mode` | varchar(20) | `'hybrid' \| 'remote' \| 'on_site'` |
| `status` | varchar(20) | NOT NULL - see status enum above |
| `created_at` | timestamptz | NOT NULL |
| `created_by` | uuid | FK -> platform_users(id) - the platform account that created the tenant |
| `activated_at` | timestamptz | Nullable - set when status transitions to active |
| `suspended_at` | timestamptz | Nullable |
| `cancelled_at` | timestamptz | Nullable |

**Indexes:** `UNIQUE(tenant_code)`, `UNIQUE(domain)`, `btree(status)`, `btree(created_at DESC)`

---

### tenant_provisioning_states (owned by: SharedPlatform)

Tracks 4-step wizard completion state. One row per tenant, created when the tenant row is created.

| Column | Type | Notes |
|---|---|---|
| `tenant_id` | uuid | PRIMARY KEY, FK -> tenants(id) |
| `step_1_complete` | boolean | NOT NULL, default false - Organization Info saved |
| `step_2_complete` | boolean | NOT NULL, default false - Admin Account set |
| `step_3_complete` | boolean | NOT NULL, default false - Subscription saved |
| `step_4_complete` | boolean | NOT NULL, default false - Configuration saved |
| `activated` | boolean | NOT NULL, default false - provision/confirm completed |
| `last_completed_step` | int | Nullable - 1–4, used to resume wizard at correct step |
| `updated_at` | timestamptz | NOT NULL |

---

### tenant_provisioning_validation_results (owned by: SharedPlatform)

Stores the most recent activation guard check results - the list of blocking items when `PATCH /provision/confirm` is attempted and fails.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `tenant_id` | uuid | FK -> tenants(id), NOT NULL |
| `checked_at` | timestamptz | NOT NULL - when the guard ran |
| `blockers` | jsonb | NOT NULL - array of `{code, message}` objects |
| `warnings` | jsonb | NOT NULL - array of `{code, message}` for non-blocking issues |
| `all_passed` | boolean | NOT NULL - true only when blockers is empty |

**Index:** `btree(tenant_id)`, `btree(checked_at DESC)`

---

### subscription_plans (owned by: SharedPlatform / Billing)

Global reusable paid plan catalog. Plans are not tenant-scoped. Current scope supports monthly and annual subscription plans only. Paid plans must not store demo/trial duration; `demo_profiles.trial_duration_days` is the source of truth for demo tenants.

| Column | Type | Notes |
|---|---|---|
| `id` | varchar(80) | PRIMARY KEY - human-readable slug e.g. `plan-enterprise-2026-v1` |
| `name` | varchar(80) | UNIQUE among active plans, NOT NULL |
| `tier` | varchar(30) | NOT NULL - `enterprise`, `business`, `professional`, or `custom` |
| `description` | text | Nullable |
| `is_active` | boolean | NOT NULL, default true |
| `included_module_keys` | text[] | NOT NULL - derived/read model array of all selected module key strings; `subscription_plan_modules` is the source of truth for base vs add-on classification |
| `shared_base_storage_gb` | int | NOT NULL, default 0 |
| `shared_base_ai_token_allowance` | bigint | NOT NULL, default 0 |
| `supported_billing_cycles` | text[] | NOT NULL - `monthly`, `annual` |
| `annual_price_override` | numeric(12,2) | Nullable |
| `annual_discount_pct` | numeric(5,2) | Nullable - discount applied to monthly x 12 for annual |
| `created_by_id` | uuid | FK -> platform_users(id) |
| `created_at` | timestamptz | NOT NULL |
| `updated_at` | timestamptz | NOT NULL |

---

### subscription_plan_price_brackets (owned by: SharedPlatform / Billing)

Company-size pricing tiers per plan. Multiple rows per plan, one per company-size or employee-count range.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `plan_id` | varchar(80) | FK -> subscription_plans(id), NOT NULL |
| `company_size_range` | varchar(20) | NOT NULL - e.g. `51-200` |
| `base_plan_monthly_price` | numeric(12,2) | NOT NULL |
| `optional_addon_prices` | jsonb | NOT NULL, default `{}` - `{module_key: monthly_price}` map |
| `resource_addon_prices` | jsonb | NOT NULL, default `{}` - `{addon_id: unit_price}` map |
| `currency` | varchar(3) | NOT NULL, ISO 4217 |
| `created_at` | timestamptz | NOT NULL |

**Unique constraint:** `(plan_id, company_size_range)`

---
### subscription_plan_modules (owned by: SharedPlatform / Billing)

Explicit package classification for selected plan modules. This table is the source of truth for whether a selected module is included in the base package or offered as an optional add-on.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `plan_id` | varchar(80) | FK -> subscription_plans(id), NOT NULL |
| `module_key` | varchar(80) | FK/logical reference -> module_catalog(module_key), NOT NULL |
| `package_type` | varchar(20) | `base` or `optional_addon`, NOT NULL |
| `storage_contribution_gb` | int | Nullable - added to shared tenant pool when applicable |
| `ai_token_contribution` | bigint | Nullable - added to tenant AI allowance when applicable |
| `is_active` | boolean | NOT NULL, default true |
| `created_at` | timestamptz | NOT NULL |

**Unique constraint:** `(plan_id, module_key)`.

**Duplicate prevention rule:** a module cannot be both base and optional add-on in the same plan. A tenant subscription must not create duplicate entitlements or duplicate charges for the same module.

---

### subscription_plan_resource_addons (owned by: SharedPlatform / Billing)

Resource-only add-ons are not modules. They increase the tenant's shared storage pool and/or shared AI token allowance.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `plan_id` | varchar(80) | FK -> subscription_plans(id), NOT NULL |
| `label` | varchar(120) | e.g. `Extra Storage Pack`, `Extra AI Token Pack` |
| `storage_contribution_gb` | int | Nullable |
| `ai_token_contribution` | bigint | Nullable |
| `price_by_employee_tier` | jsonb | NOT NULL - `{employee_count_tier: unit_price}` |
| `is_active` | boolean | NOT NULL, default true |
| `created_at` | timestamptz | NOT NULL |

---

### demo_profiles (owned by: SharedPlatform / Developer Platform)

Controls demo/trial tenant behavior and the upgrade choices visible to demo customers.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `name` | varchar(120) | NOT NULL |
| `trial_duration_days` | int | NOT NULL |
| `auto_expire` | boolean | NOT NULL, default true |
| `max_employees` | int | NOT NULL |
| `demo_storage_limit_gb` | int | NOT NULL |
| `demo_ai_token_limit` | bigint | Nullable |
| `is_active` | boolean | NOT NULL, default true |
| `created_by_id` | uuid | FK -> platform_users(id) |
| `created_at` | timestamptz | NOT NULL |
| `updated_at` | timestamptz | NOT NULL |

---

### demo_profile_modules

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `demo_profile_id` | uuid | FK -> demo_profiles(id), NOT NULL |
| `module_key` | varchar(80) | NOT NULL |
| `access_level` | varchar(20) | `full_access`, `view_only`, or `archive` |
| `feature_permissions` | jsonb | NOT NULL, default `{}` |

**Unique constraint:** `(demo_profile_id, module_key)`.

---

### demo_profile_upgrade_options

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `demo_profile_id` | uuid | FK -> demo_profiles(id), NOT NULL |
| `allowed_plan_ids` | text[] | NOT NULL |
| `allowed_addon_module_keys` | text[] | NOT NULL, default `{}` |
| `hidden_addon_module_keys` | text[] | NOT NULL, default `{}` |
| `addon_visibility` | jsonb | NOT NULL - `{module_key: "enabled" | "show_only"}` |
| `addon_demo_limits` | jsonb | NOT NULL, default `{}` |

---

### tenant_resource_limits

Effective shared resource limits for a tenant after applying demo profile, selected plan, selected add-ons, resource-only add-ons, and approved tenant overrides.

| Column | Type | Notes |
|---|---|---|
| `tenant_id` | uuid | PRIMARY KEY / FK -> tenants(id) |
| `storage_limit_gb` | int | NOT NULL |
| `ai_token_limit` | bigint | Nullable |
| `source` | varchar(30) | `demo_profile`, `subscription_plan`, `subscription_addons`, `tenant_override` |
| `updated_at` | timestamptz | NOT NULL |

---

### Paid activation storage rule

There is no paid activation request table. Demo upgrade and paid activation are customer self-service flows: the tenant owner confirms company details, actual employee count, selected plan/add-ons, billing cycle, and billing contact; the system creates the subscription/payment snapshot and first invoice; the tenant becomes active after payment succeeds.

Requests Center stores only `demo_access_requests` and `trial_extension_requests`.

---

### demo_access_requests

Public/demo inquiry requests that require platform-side approval before a demo tenant is created or updated. This is request intake only: submitting this record does not create a tenant, user account, session, or entitlement. This table is only for demo access review. It is not used for paid activation.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `requester_name` | varchar(160) | NOT NULL |
| `requester_email` | varchar(255) | NOT NULL |
| `requester_phone` | varchar(50) | Nullable |
| `company_name` | varchar(200) | NOT NULL |
| `requested_subdomain` | varchar(120) | Nullable; desired tenant subdomain |
| `company_website` | varchar(255) | Nullable |
| `company_size_range` | varchar(30) | Nullable; applicant-provided estimate |
| `country_code` | char(2) | Nullable FK -> countries(iso2_code) |
| `requested_demo_profile_id` | uuid | Nullable FK -> demo_profiles(id) |
| `requested_module_keys` | text[] | NOT NULL, default `{}` |
| `requested_access_notes` | text | Nullable |
| `status` | varchar(30) | `pending_review`, `approved`, `rejected`, `cancelled` |
| `submitted_at` | timestamptz | NOT NULL |
| `reviewed_by_id` | uuid | Nullable FK -> platform_users(id) |
| `reviewed_at` | timestamptz | Nullable |
| `admin_notes` | text | Nullable; internal review notes |
| `tenant_visible_note` | text | Nullable; sent to applicant on approve/reject |
| `created_tenant_id` | uuid | Nullable FK -> tenants(id); set after approval creates/updates demo tenant |
| `source` | varchar(40) | Nullable; website, sales, manual_admin, partner |
| `metadata` | jsonb | Nullable; campaign/source context, UTM, sales notes |

**Indexes / Constraints:**

- Unique pending request by requester email + company name should be enforced at application level first; database may add a partial unique index after final duplicate policy is confirmed.
- Index `(status, submitted_at)` for Requests Center queues.
- Index `(requester_email)` for duplicate checks and applicant history.

---

### trial_extension_requests

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `tenant_id` | uuid | FK -> tenants(id), NOT NULL |
| `current_trial_end_at` | timestamptz | NOT NULL |
| `requested_days` | int | NOT NULL |
| `approved_days` | int | Nullable |
| `reason` | text | NOT NULL |
| `usage_snapshot` | jsonb | Storage, AI token usage, login count, last login |
| `status` | varchar(30) | `pending_review`, `approved`, `rejected` |
| `requested_at` | timestamptz | NOT NULL |
| `reviewed_by_id` | uuid | Nullable FK -> platform_users(id) |
| `reviewed_at` | timestamptz | Nullable |
| `admin_notes` | text | Nullable |

---

### support_tickets

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `tenant_id` | uuid | FK -> tenants(id), NOT NULL |
| `subject` | varchar(200) | NOT NULL |
| `description` | text | NOT NULL |
| `category` | varchar(80) | NOT NULL |
| `priority` | varchar(20) | NOT NULL |
| `status` | varchar(30) | `open`, `in_progress`, `waiting_for_customer`, `resolved` |
| `created_by_user_id` | uuid | Tenant user id |
| `assigned_to_id` | uuid | Nullable FK -> platform_users(id) |
| `last_customer_reply_at` | timestamptz | Nullable |
| `last_platform_reply_at` | timestamptz | Nullable |
| `last_activity_at` | timestamptz | NOT NULL |
| `resolved_by_id` | uuid | Nullable FK -> platform_users(id) |
| `created_at` | timestamptz | NOT NULL |
| `updated_at` | timestamptz | NOT NULL |
| `resolved_at` | timestamptz | Nullable |

Support messages, internal notes, timeline events, and attachments are stored in separate child records so customer-visible communication is not mixed with internal-only notes.

---

### support_ticket_messages

Customer-visible support conversation entries between tenant users and platform support users.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `support_ticket_id` | uuid | FK -> support_tickets(id), NOT NULL |
| `tenant_id` | uuid | FK -> tenants(id), NOT NULL |
| `sender_type` | varchar(30) | `tenant_user`, `platform_user`, `system` |
| `sender_user_id` | uuid | Nullable FK -> users(id); required when `sender_type = tenant_user` |
| `sender_platform_user_id` | uuid | Nullable FK -> platform_users(id); required when `sender_type = platform_user` |
| `message_body` | text | NOT NULL |
| `message_format` | varchar(20) | `text`, `markdown` |
| `is_customer_visible` | boolean | Always true for tenant/platform replies returned to tenant APIs |
| `created_at` | timestamptz | NOT NULL |
| `updated_at` | timestamptz | Nullable |
| `edited_at` | timestamptz | Nullable |
| `deleted_at` | timestamptz | Nullable; soft delete |

Rules:
- Tenant-facing APIs return only non-deleted customer-visible messages.
- `sender_type = tenant_user` requires `sender_user_id`.
- `sender_type = platform_user` requires `sender_platform_user_id`.
- Reply creation also appends a `support_ticket_events` row.

---

### support_ticket_internal_notes

Platform-only notes for support investigation. These notes are never returned by tenant-facing support APIs.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `support_ticket_id` | uuid | FK -> support_tickets(id), NOT NULL |
| `tenant_id` | uuid | FK -> tenants(id), NOT NULL |
| `author_platform_user_id` | uuid | FK -> platform_users(id), NOT NULL |
| `note_body` | text | NOT NULL |
| `created_at` | timestamptz | NOT NULL |
| `updated_at` | timestamptz | Nullable |
| `edited_at` | timestamptz | Nullable |
| `deleted_at` | timestamptz | Nullable; soft delete |

Rules:
- Requires `platform.support.manage`.
- Tenant-facing APIs must never return this table.
- Note creation also appends a `support_ticket_events` row.

---

### support_ticket_events

Activity timeline for support ticket lifecycle changes, customer-visible replies, internal note creation, attachment changes, and closure.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `support_ticket_id` | uuid | FK -> support_tickets(id), NOT NULL |
| `tenant_id` | uuid | FK -> tenants(id), NOT NULL |
| `event_type` | varchar(80) | e.g. `ticket.created`, `ticket.assigned`, `ticket.reply_added`, `ticket.internal_note_added`, `ticket.category_changed`, `ticket.status_changed`, `ticket.resolved`, `ticket.attachment_added` |
| `actor_type` | varchar(30) | `tenant_user`, `platform_user`, `system` |
| `actor_user_id` | uuid | Nullable FK -> users(id) |
| `actor_platform_user_id` | uuid | Nullable FK -> platform_users(id) |
| `old_values_json` | jsonb | Nullable previous state snapshot |
| `new_values_json` | jsonb | Nullable new state snapshot |
| `metadata_json` | jsonb | Nullable safe non-secret metadata |
| `created_at` | timestamptz | NOT NULL |

Rules:
- Used for the ticket activity timeline shown in Developer Platform.
- Audit-critical actions also write to the shared audit log where required by platform audit policy.

---

### subscription_plan_price_history (owned by: SharedPlatform / Billing)

Immutable log of every price bracket change. Never updated, only inserted.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `plan_id` | varchar(80) | FK -> subscription_plans(id), NOT NULL |
| `employee_count_tier` | varchar(20) | NOT NULL |
| `module_key` | varchar(80) | NOT NULL - which module's price changed |
| `previous_unit_price` | numeric(12,2) | NOT NULL |
| `new_unit_price` | numeric(12,2) | NOT NULL |
| `changed_by_id` | uuid | FK -> platform_users(id), NOT NULL |
| `changed_at` | timestamptz | NOT NULL |
| `reason` | text | Nullable |

---

### tenant_subscriptions (owned by: SharedPlatform / Billing)

Commercial snapshot per tenant. One active row per tenant. Changes create a new row and archive the old one.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `tenant_id` | uuid | FK -> tenants(id), NOT NULL |
| `plan_id` | varchar(80) | FK -> subscription_plans(id), NOT NULL |
| `is_current` | boolean | NOT NULL - only one true per tenant |
| `billing_cycle` | varchar(10) | `monthly` or `annual` |
| `billing_start_date` | date | NOT NULL |
| `next_billing_date` | date | Nullable - calculated from billing_start + cycle |
| `billing_end_date` | date | Nullable - when contract ends |
| `confirmed_employee_count` | int | NOT NULL - used for first invoice and company-size bracket |
| `selected_base_module_keys` | text[] | NOT NULL - snapshot from selected plan |
| `selected_addon_module_keys` | text[] | NOT NULL, default empty |
| `selected_resource_addons` | jsonb | NOT NULL, default `[]` |
| `calculated_monthly_amount` | numeric(12,2) | NOT NULL |
| `calculated_annual_amount` | numeric(12,2) | Nullable |
| `annual_price_override` | numeric(12,2) | Nullable |
| `annual_discount_pct` | numeric(5,2) | Nullable |
| `effective_amount` | numeric(12,2) | NOT NULL |
| `currency` | varchar(3) | NOT NULL |
| `status` | varchar(30) | `pending_payment`, `active`, `grace_period`, `suspended`, or `cancelled` |
| `cancellation_requested_at` | timestamptz | Nullable |
| `unpaid_seat_dues_amount` | numeric(12,2) | NOT NULL, default 0 |
| `payment_gateway_config_id` | uuid | FK -> payment_gateway_configs(id), NOT NULL |
| `created_by_user_id` | uuid | Nullable FK -> users(id); tenant self-service actor |
| `created_by_platform_user_id` | uuid | Nullable FK -> platform_users(id); platform-operator actor |
| `created_at` | timestamptz | NOT NULL |
| `archived_at` | timestamptz | Nullable - set when superseded by new row |

**Index:** `btree(tenant_id, is_current)`, `btree(next_billing_date)`, `btree(status)`

**Actor rule:** exactly one of `created_by_user_id` or `created_by_platform_user_id` must be set.

---

### tenant_subscription_events (owned by: SharedPlatform / Billing)

Audit history for tenant self-service and platform-operator subscription changes.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `tenant_subscription_id` | uuid | FK -> tenant_subscriptions(id), NOT NULL |
| `tenant_id` | uuid | FK -> tenants(id), NOT NULL |
| `event_type` | varchar(80) | `created`, `plan_changed`, `addons_changed`, `billing_cycle_changed`, `cancel_requested`, `platform_adjusted` |
| `actor_user_id` | uuid | Nullable FK -> users(id) |
| `actor_platform_user_id` | uuid | Nullable FK -> platform_users(id) |
| `old_values_json` | jsonb | Nullable previous commercial snapshot |
| `new_values_json` | jsonb | New commercial snapshot |
| `reason` | text | Nullable tenant reason or required platform operator reason depending on event type |
| `created_at` | timestamptz | NOT NULL |

**Actor rule:** exactly one of `actor_user_id` or `actor_platform_user_id` must be set.

---
### tenant_module_entitlements (owned by: SharedPlatform)

Runtime access source of truth. One row per module per tenant. This table - not the subscription snapshot - is what the ONEVO application checks to determine if a tenant may access a module.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `tenant_id` | uuid | FK -> tenants(id), NOT NULL |
| `module_key` | varchar(80) | FK -> module_catalog(module_key), NOT NULL |
| `status` | varchar(30) | NOT NULL - see entitlement status enum |
| `sales_state` | varchar(30) | NOT NULL - see sales state enum |
| `runtime_override` | boolean | Nullable runtime-only override; `NULL` inherits commercial entitlement, `false` force-disables runtime access, `true` explicitly restores runtime access without bypassing commercial entitlement |
| `unit_price` | numeric(12,2) | Nullable - module-specific override price |
| `currency` | varchar(3) | Nullable |
| `start_date` | date | Nullable |
| `end_date` | date | Nullable - subscription or entitlement end |
| entitlement_source | varchar(30) | NOT NULL - 'plan_included' | 'add_on' | 'operator_grant' |
| `created_by_user_id` | uuid | Nullable FK -> users(id); tenant self-service actor |
| `created_by_platform_user_id` | uuid | Nullable FK -> platform_users(id); platform-operator actor |
| `created_at` | timestamptz | NOT NULL |
| `updated_at` | timestamptz | NOT NULL |

**Unique constraint:** `(tenant_id, module_key)`
**Index:** `btree(tenant_id, status)` - queried on every permission resolution
**Actor rule:** exactly one of `created_by_user_id` or `created_by_platform_user_id` must be set when the entitlement is created by a human actor; system-derived entitlement changes link back to the subscription event that caused them.
**Runtime rule:** Module runtime access requires an active commercial entitlement and `runtime_override IS DISTINCT FROM false`. A `true` override does not grant access when the module is not commercially entitled.

**Entitlement status enum:**
| Value | Meaning |
|---|---|
| `provisioning` | Set during wizard - not yet active; tenant cannot access module |
| `active` | Tenant has runtime access |
| `suspended` | Access paused (e.g. payment failure) |
| `disabled` | Explicitly turned off - not accessible |

**Sales state enum:**
| Value | Meaning |
|---|---|
| `subscription_included` | Part of the subscription plan |
| `purchased` | Purchased optional module add-on |

| `quoted` | Quoted to customer - not yet purchased; no access |
| `available` | In catalog, can be purchased - not yet active; no access |
| `disabled` | Not accessible and not in sales pipeline |

---

### payment_gateway_configs (owned by: SharedPlatform / Billing)

Payment gateway metadata. Gateway credentials are stored in `payment_gateway_credentials`, and country routing is stored in `payment_gateway_country_routes`: one gateway config can be routed to many countries, but one country can have only one active gateway route per environment.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `gateway_key` | varchar(80) | UNIQUE NOT NULL - operator-set readable slug, e.g. `'paddle-global-prod'` |
| `provider` | varchar(20) | NOT NULL - `stripe`, `paddle`, or `payhere` |
| `display_name` | varchar(100) | NOT NULL - friendly operator label |
| `logo_url` | varchar(500) | Nullable - uploaded via `POST /admin/v1/uploads/gateway-logo`; shown in System Config payment provider records |
| `environment` | varchar(20) | NOT NULL - `'sandbox' \| 'production'` |
| `public_key` | varchar(255) | Nullable; provider public identifier where applicable |
| `merchant_id` | varchar(100) | Nullable; Paddle seller ID or PayHere merchant ID |
| `webhook_url` | varchar(500) | Gateway callback/notify URL |
| `is_active` | boolean | NOT NULL, default true |
| `created_by_id` | uuid | FK -> platform_users(id), NOT NULL |
| `created_at` | timestamptz | NOT NULL |
| `updated_at` | timestamptz | NOT NULL |

**Rule:** Gateway selection is resolved through active `payment_gateway_country_routes`. Do not add `is_default` to this table.

---

### payment_gateway_credentials (owned by: SharedPlatform / Billing)

Encrypted credential versions for a payment gateway config. A new secret creates a new credential row; previous rows are deactivated instead of overwritten.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `payment_gateway_config_id` | uuid | FK -> payment_gateway_configs(id), NOT NULL |
| `secret_encrypted` | text | NOT NULL - AES-256; Stripe secret key, Paddle API key, or PayHere merchant secret |
| `webhook_secret_encrypted` | text | Nullable - AES-256 webhook signing secret |
| `encryption_key_version` | varchar(50) | NOT NULL |
| `credential_version` | int | NOT NULL - monotonic per gateway config |
| `is_active` | boolean | NOT NULL, default true |
| `rotated_by_id` | uuid | FK -> platform_users(id), NOT NULL |
| `rotated_at` | timestamptz | NOT NULL |
| `deactivated_by_id` | uuid | Nullable FK -> platform_users(id) |
| `deactivated_at` | timestamptz | Nullable |

**Business rule:** one active credential row per `payment_gateway_config_id`. Business tables reference the gateway config, not credential rows.

---

### payment_gateway_country_routes (owned by: SharedPlatform / Billing)

Country-to-gateway routing for tenant payment collection. Operators select country names in the UI; backend stores ISO country codes.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `country_code` | varchar(2) | ISO 3166-1 alpha-2, NOT NULL |
| `country_name_snapshot` | varchar(120) | Display snapshot for audit/readability |
| `gateway_config_id` | uuid | FK -> payment_gateway_configs(id), NOT NULL |
| `environment` | varchar(20) | NOT NULL - `'sandbox' \| 'production'` |
| `is_active` | boolean | NOT NULL, default true |
| `created_by_id` | uuid | FK -> platform_users(id), NOT NULL |
| `created_at` | timestamptz | NOT NULL |
| `updated_at` | timestamptz | NOT NULL |

**Business rule:** one active route per `country_code + environment`. A gateway config may have multiple country route rows.

---

### subscription_invoices (owned by: SharedPlatform / Billing)

Invoice records for all tenant billing cycles.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `invoice_number` | varchar(50) | UNIQUE, NOT NULL - format `INV-{tenant_code}-{YYYYMM}-{seq}` |
| `tenant_id` | uuid | FK -> tenants(id), NOT NULL |
| `subscription_id` | uuid | FK -> tenant_subscriptions(id), NOT NULL |
| `payment_gateway_config_id` | uuid | FK -> payment_gateway_configs(id), NOT NULL |
| `billing_period_start` | date | NOT NULL |
| `billing_period_end` | date | NOT NULL |
| `line_items` | jsonb | NOT NULL - array of `{module_key, name, unit_price, quantity, pricing_unit, line_total}` |
| `subtotal` | numeric(12,2) | NOT NULL |
| `calculated_price` | numeric(12,2) | NOT NULL |
| `override_price` | numeric(12,2) | Nullable |
| `effective_price` | numeric(12,2) | NOT NULL |
| `tax_amount` | numeric(12,2) | NOT NULL, default 0 |
| `total` | numeric(12,2) | NOT NULL |
| `currency` | varchar(3) | NOT NULL |
| `status` | varchar(20) | NOT NULL - `'draft' \| 'open' \| 'paid' \| 'overdue' \| 'void' \| 'uncollectible' \| 'partially_refunded'` |
| `due_date` | date | NOT NULL |
| `external_invoice_id` | varchar(100) | Nullable gateway invoice ID from Stripe, Paddle, or PayHere |
| `external_payment_reference` | varchar(200) | Nullable gateway payment/charge reference |
| `external_invoice_url` | varchar(500) | Nullable gateway-hosted invoice PDF URL |
| `payment_attempt_count` | int | NOT NULL, default 0 - incremented per gateway retry |
| `created_at` | timestamptz | NOT NULL |
| `updated_at` | timestamptz | NOT NULL |

**Index:** `btree(tenant_id, status)`, `btree(due_date)`, `btree(payment_gateway_config_id)`, `UNIQUE(invoice_number)`

---

### webhook_event_queue (owned by: SharedPlatform / Billing)
Reliable event processing queue for inbound Stripe, Paddle, and PayHere webhooks. Ensures at-least-once processing with dead-letter tracking.

| Column | Type | Notes |
|---|---|---|
| `provider` | varchar(20) | NOT NULL - `stripe`, `paddle`, or `payhere` |
| `event_id` | varchar(100) | UNIQUE, NOT NULL - provider event/order ID; idempotency key |
| `event_type` | varchar(100) | NOT NULL - e.g. `'payment_intent.succeeded'` |
| `payload` | jsonb | NOT NULL - full webhook payload |
| `status` | varchar(20) | NOT NULL - `'pending' \| 'processing' \| 'completed' \| 'failed' \| 'dead_letter'` |
| `attempt_count` | int | NOT NULL, default 0 |
| `last_attempt_at` | timestamptz | Nullable |
| `next_retry_at` | timestamptz | Nullable - exponential backoff schedule |
| `error_message` | text | Nullable - last processing error |
| `received_at` | timestamptz | NOT NULL |
| `completed_at` | timestamptz | Nullable |

**Index:** `btree(status, next_retry_at)`, `UNIQUE(provider, event_id)`

---

### platform_alerts (owned by: DevPlatform)


| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `alert_code` | varchar(80) | NOT NULL - machine-readable code from the alert catalog |
| `severity` | varchar(10) | NOT NULL - `'critical' \| 'warning' \| 'info'` |
| `tenant_id` | uuid | Nullable, FK -> tenants(id) - null for platform-level alerts |
| `source_module` | varchar(80) | NOT NULL - module key that raised the alert |
| `title` | varchar(200) | NOT NULL - human-readable summary |
| `detail` | text | Nullable - additional context (IPs, counts, thresholds, etc.) |
| `created_at` | timestamptz | NOT NULL |
| `auto_resolved` | boolean | NOT NULL, default false |
| `resolved_at` | timestamptz | Nullable |
| `resolved_by_id` | uuid | Nullable, FK -> platform_users(id) |
| `resolved_reason` | text | Nullable - required for Critical severity |
| `acknowledged_at` | timestamptz | Nullable |
| `acknowledged_by_id` | uuid | Nullable, FK -> platform_users(id) |
| `auto_dismissed` | boolean | NOT NULL, default false - Info alerts dismissed after 48h |

**Index:** `btree(severity, created_at DESC)`, `btree(tenant_id, severity)`, `btree(alert_code)`, partial index on `(resolved_at IS NULL)` for active alert queries

---

### legal_document_versions (owned by: DevPlatform / Compliance)

Published legal and privacy document versions managed from Compliance Center.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `document_type` | varchar(80) | `terms`, `privacy_notice`, `activity_monitoring_notice`, `screenshot_notice`, `biometric_photo_consent`, or `marketing` |
| `version` | varchar(50) | Stable version shown to users and stored in `legal_acceptance_records.document_version` |
| `title` | varchar(200) | Display title |
| `content_url` | varchar(500) | Stored document URL or rendered content reference |
| `is_required` | boolean | Whether acknowledgement/acceptance is required |
| `block_scope` | varchar(40) | `dashboard`, `workpulse_collection`, `verification`, or `none` |
| `status` | varchar(20) | `draft`, `published`, or `archived` |
| `published_by_id` | uuid | FK -> platform_users(id), nullable until published |
| `published_at` | timestamptz | Nullable |
| `publish_reason` | text | Required when publishing |
| `created_at` | timestamptz | NOT NULL |
| `updated_at` | timestamptz | NOT NULL |

**Rule:** Publishing required Terms & Conditions or Privacy Notice versions marks affected users pending and blocks dashboard access until accepted or acknowledged. Publishing required monitoring, screenshot, or biometric/photo versions blocks only the affected WorkPulse collection or verification path.

---

### feature_flags (owned by: Configuration)

Global feature flag definitions. Tenant-specific overrides are managed from Tenant Management -> Tenant Detail -> Runtime Overrides, not from a top-level Feature Flags sidebar item.

| Column | Type | Notes |
|---|---|---|
| `key` | varchar(120) | PRIMARY KEY |
| `description` | text | Nullable |
| `default_value` | boolean | NOT NULL |
| `rollout_percentage` | int | NOT NULL, 0–100 - % of tenants that get this flag as ON globally |
| `module_key` | varchar(80) | Nullable FK -> module_catalog(module_key) - which module this flag gates |
| `feature_key` | varchar(120) | Nullable FK -> module_features(feature_key) - commercial feature this flag controls at runtime |
| `is_active` | boolean | NOT NULL, default true |
| `created_at` | timestamptz | NOT NULL |
| `updated_at` | timestamptz | NOT NULL |

**Linkage rule:** Tenant-facing product feature flags must set both `module_key` and `feature_key`, and `feature_key` must reference a feature owned by that module in `module_features`. Only platform operational flags that are not sold as tenant features may keep `module_key` and `feature_key` null.

---

### feature_flag_overrides (owned by: Configuration)

Per-tenant feature flag overrides. Overrides the global default for a specific tenant after commercial entitlement and feature inclusion pass.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `flag_key` | varchar(120) | FK -> feature_flags(key), NOT NULL |
| `tenant_id` | uuid | FK -> tenants(id), NOT NULL |
| `value` | boolean | NOT NULL - the overridden value for this tenant |
| `granted_by_id` | uuid | FK -> platform_users(id), NOT NULL |
| `granted_at` | timestamptz | NOT NULL |
| `reason` | text | Nullable |

**Unique constraint:** `(flag_key, tenant_id)`

---

### users (owned by: Auth - shown here for cross-reference)

Tenant-scoped user accounts. Every user belongs to exactly one tenant. **Admin-invited users** have `status = 'invited'` until they complete set-password via invite link.

Key columns relevant to Developer Platform operations:

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `tenant_id` | uuid | FK -> tenants(id), NOT NULL - always tenant-scoped |
| `email` | varchar(255) | NOT NULL |
| `first_name` | varchar(50) | NOT NULL |
| `last_name` | varchar(50) | NOT NULL |
| `status` | varchar(20) | `'invited' \| 'active' \| 'suspended' \| 'deactivated'` |
| `role_label` | varchar(80) | Label from provisioning - actual permissions from roles/role_permissions |
| `work_mode` | varchar(20) | `'hybrid' \| 'remote' \| 'on_site'` |
| `invite_sent_at` | timestamptz | Nullable |
| `invite_expires_at` | timestamptz | Nullable - 72 hours from invite_sent_at |
| `send_invite_on_activation` | boolean | NOT NULL, default true |
| `last_login_at` | timestamptz | Nullable |
| `created_at` | timestamptz | NOT NULL |

**Multi-tenant email rule:** Same email can exist in `users` across multiple tenants with different `tenant_id`. This is enforced at application layer - each user+tenant pair is independent.

---

---

## Integration & AI Provider Tables

### ai_provider_configs (owned by: DevPlatform)

Global AI provider configuration per purpose. One row per ONEVO AI feature purpose (`ai_insights`, `report_generation`, and Phase 2 `agentic_chat`). No hardcoded provider names or model names - all operator-configured.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `config_name` | varchar(80) | NOT NULL - operator-chosen label |
| `logo_url` | varchar(500) | Nullable - uploaded via `POST /admin/v1/uploads/ai-provider-logo` |
| `purpose` | varchar(40) | UNIQUE NOT NULL - `'ai_insights' \| 'report_generation' \| 'agentic_chat' (Phase 2)` |
| `provider_format` | varchar(30) | NOT NULL - `'openai_compatible' \| 'anthropic'` - API request/response shape only |
| `api_base_url` | varchar(500) | NOT NULL - always required; no default |
| `model` | varchar(120) | NOT NULL - set from provider's model fetch, not typed free-form |
| `api_key_encrypted` | text | NOT NULL - AES-256; never returned by API |
| `request_timeout_seconds` | int | NOT NULL, default 60 |
| `max_retries` | int | NOT NULL, default 2 |
| `is_active` | boolean | NOT NULL, default true |
| `last_verified_at` | timestamptz | Nullable |
| `last_verification_status` | varchar(20) | Nullable - `'healthy' \| 'error'` |
| `updated_by_id` | uuid | FK -> platform_users(id) |
| `updated_at` | timestamptz | NOT NULL |

**Index:** `UNIQUE(purpose)`

---

### tenant_ai_provider_overrides (owned by: DevPlatform)

Per-tenant AI config overrides. One row per (tenant, purpose) pair. When present and active, takes precedence over global `ai_provider_configs` for that tenant.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `tenant_id` | uuid | FK -> tenants(id), NOT NULL |
| `purpose` | varchar(40) | NOT NULL |
| `config_name` | varchar(80) | NOT NULL |
| `provider_format` | varchar(30) | NOT NULL |
| `api_base_url` | varchar(500) | NOT NULL |
| `model` | varchar(120) | NOT NULL |
| `api_key_encrypted` | text | NOT NULL - AES-256 |
| `request_timeout_seconds` | int | NOT NULL |
| `max_retries` | int | NOT NULL |
| `is_active` | boolean | NOT NULL, default true |
| `set_by_id` | uuid | FK -> platform_users(id), NOT NULL |
| `set_at` | timestamptz | NOT NULL |

**Unique:** `(tenant_id, purpose)`

---

### platform_oauth_apps (owned by: DevPlatform)

ONEVO's OAuth app registrations used when tenants or employees connect integrations via the ONEVO app consent flow. One row per provider. These are ONEVO's developer app metadata - not the tenant's tokens. Secrets are stored in `platform_oauth_app_credentials`.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `provider` | varchar(30) | UNIQUE NOT NULL - operator-set slug, e.g. `'github'`, `'zoom'`, `'microsoft'`, `'google'` (Slack is Phase 2) |
| `app_name` | varchar(100) | NOT NULL - shown in OAuth consent screen |
| `logo_url` | varchar(500) | Nullable - uploaded via `POST /admin/v1/uploads/oauth-app-logo`; stored in platform file storage |
| `client_id` | varchar(200) | NOT NULL - not encrypted; used in redirect URLs |
| `authorization_url` | varchar(500) | NOT NULL |
| `token_url` | varchar(500) | NOT NULL |
| `default_scopes` | text[] | NOT NULL |
| `is_active` | boolean | NOT NULL |
| `last_verified_at` | timestamptz | Nullable |
| `updated_by_id` | uuid | FK -> platform_users(id) |
| `updated_at` | timestamptz | NOT NULL |

**Index:** `UNIQUE(provider)`

---

### platform_oauth_app_credentials (owned by: DevPlatform)

Encrypted credential versions for ONEVO's OAuth app registrations. A new OAuth secret creates a new credential row; previous rows are deactivated instead of overwritten.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `platform_oauth_app_id` | uuid | FK -> platform_oauth_apps(id), NOT NULL |
| `client_secret_encrypted` | text | NOT NULL - AES-256 |
| `private_key_encrypted` | text | Nullable - GitHub App private key or provider-specific secret material |
| `encryption_key_version` | varchar(50) | NOT NULL |
| `credential_version` | int | NOT NULL - monotonic per OAuth app |
| `is_active` | boolean | NOT NULL, default true |
| `rotated_by_id` | uuid | FK -> platform_users(id), NOT NULL |
| `rotated_at` | timestamptz | NOT NULL |
| `deactivated_by_id` | uuid | Nullable FK -> platform_users(id) |
| `deactivated_at` | timestamptz | Nullable |

**Business rule:** one active credential row per `platform_oauth_app_id`. Tenant-scope connected integration tokens (`connection_scope = 'tenant'`) are stored in `tenant_integration_credentials`. Employee-scope tokens (`connection_scope = 'employee'`) such as Google/Outlook Calendar live in `external_calendar_connections` with calendar sync state.

---

### platform_service_keys (owned by: DevPlatform)

ONEVO's own third-party service API keys used internally across all tenants (Resend, Cloudflare, etc.).

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `service_key` | varchar(50) | UNIQUE NOT NULL - e.g. `'resend'`, `'cloudflare'`, `'cloudflare_r2'` |
| `display_name` | varchar(80) | NOT NULL |
| `api_key_encrypted` | text | NOT NULL - AES-256 |
| `is_active` | boolean | NOT NULL |
| `last_verified_at` | timestamptz | Nullable |
| `updated_by_id` | uuid | FK -> platform_users(id) |
| `updated_at` | timestamptz | NOT NULL |

**Index:** `UNIQUE(service_key)`

---

### integration_catalog (owned by: SharedPlatform)

Operator-managed catalog of connectable software integrations shown in the main ONEVO app. Fully dynamic - operators create entries here, nothing is hardcoded in the ONEVO application. Stores metadata only - does not store provider secrets, tenant tokens, or employee tokens. Resend, Cloudflare, Stripe, Paddle, PayHere, and biometric terminals are NOT Integration Catalog entries.

| Column | Type | Notes |
|---|---|---|
| `integration_key` | varchar(50) | PRIMARY KEY - operator-set slug, e.g. `'github'`, `'ms_teams'` |
| `display_name` | varchar(100) | NOT NULL |
| `description` | text | Nullable |
| `connection_scope` | varchar(20) | NOT NULL - `'tenant'` (token stored in `tenant_integration_credentials`) \| `'employee'` (token stored in `external_calendar_connections`) |
| `onevo_app_provider` | varchar(30) | NOT NULL FK -> platform_oauth_apps(provider) - which ONEVO OAuth app registration handles the consent flow |
| `logo_url` | varchar(500) | Nullable |
| `is_active` | boolean | NOT NULL, default true |
| `created_by_id` | uuid | FK -> platform_users(id) |
| `created_at` | timestamptz | NOT NULL |

---

### module_integration_links (owned by: SharedPlatform)

Links ONEVO product modules to integration catalog entries. Managed through Module Catalog Manager → module detail → Integrations tab. Controls visibility/connectability only - does not store credentials or tokens.

| Column | Type | Notes |
|---|---|---|
| `module_key` | varchar(80) | FK -> module_catalog(module_key), NOT NULL |
| `integration_key` | varchar(50) | FK -> integration_catalog(integration_key), NOT NULL |
| `linked_by_id` | uuid | FK -> platform_users(id), NOT NULL |
| `linked_at` | timestamptz | NOT NULL |

**Primary key:** `(module_key, integration_key)`
**Read as:** "When a tenant is entitled to `module_key`, integration `integration_key` becomes visible/connectable to them."

---

### tenant_integration_credentials (owned by: Auth / SharedPlatform)

Stores per-tenant connected integration tokens and connection state for tenant-scope integrations (`connection_scope = 'tenant'`). Written when a tenant's user completes a tenant-level consent flow. Read by the main ONEVO app to call integration APIs on behalf of the tenant. Employee-level Google/Outlook Calendar sync tokens are not stored here; they live in `external_calendar_connections`.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `tenant_id` | uuid | FK -> tenants(id), NOT NULL |
| `integration_key` | varchar(50) | FK -> integration_catalog(integration_key), NOT NULL |
| `access_token_encrypted` | text | Nullable - AES-256; refreshed automatically before expiry |
| `refresh_token_encrypted` | text | Nullable - AES-256 |
| `token_expires_at` | timestamptz | Nullable |
| `scopes_granted` | text[] | Scopes the customer actually authorised during OAuth |
| `external_account_id` | varchar(200) | Nullable - GitHub org ID, Microsoft tenant ID, Google workspace ID, etc. |
| `external_account_name` | varchar(200) | Nullable - human-readable name of the connected account |
| `status` | varchar(20) | NOT NULL - `'connected' \| 'error' \| 'expired' \| 'disconnected'` |
| `last_sync_at` | timestamptz | Nullable |
| `error_message` | text | Nullable - last error from provider |
| `connected_at` | timestamptz | NOT NULL |
| `connected_by_user_id` | uuid | FK -> users(id) - which tenant user completed the OAuth |
| `disconnected_at` | timestamptz | Nullable |

**Unique:** `(tenant_id, integration_key)` - one connection per integration per tenant
**Index:** `btree(tenant_id, status)`, `btree(integration_key)`

---

## Schema Impact Summary (Updated)

| Phase | New Tables Added | Running Total |
|---|---|---|
| Baseline | - | 170 |
| DevPlatform Phase 1 | `platform_users`, `platform_user_invites`, `platform_roles`, `platform_permissions`, `platform_role_permissions`, `platform_user_roles`, `platform_user_sessions`, `platform_alerts`, `webhook_event_queue` | Finalized by Phase 1 migration cut |
| DevPlatform Phase 2 | `agent_version_releases`, `agent_deployment_rings`, `agent_deployment_ring_assignments`, `platform_api_keys` | Finalized by Phase 2 migration cut |
| Cross-module additions | `tenant_provisioning_states`, `tenant_provisioning_validation_results` | 185 |
| AI / Gateway / Integration | `ai_provider_configs`, `tenant_ai_provider_overrides`, `payment_gateway_credentials`, `platform_oauth_apps`, `platform_oauth_app_credentials`, `platform_service_keys`, `integration_catalog`, `module_integration_links`, `tenant_integration_credentials` | 194 |
| Billing additions | `billing_audit_logs` | 195 |
| Permission catalog | `platform_permission_catalog` | 196 |
| Customer support additions | `support_tickets`, `support_ticket_messages`, `support_ticket_internal_notes`, `support_ticket_events` | 200 |

**Note:** `subscription_plans`, `subscription_plan_price_brackets`, `subscription_plan_price_history`, `tenant_subscriptions`, `tenant_module_entitlements`, `module_catalog`, `payment_gateway_configs`, `payment_gateway_credentials`, `subscription_invoices`, `feature_flags`, `feature_flag_overrides`, `feature_access_grants`, `users` are existing SharedPlatform/Auth/Billing tables. Authoritative definitions live in `database/schemas/`.

---

### billing_audit_logs (owned by: SharedPlatform / Billing)

Immutable append-only audit trail for all billing mutations. No UPDATE or DELETE permitted on this table.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `tenant_id` | uuid | FK -> tenants(id), NOT NULL |
| `actor_id` | uuid | FK -> platform_users(id), Nullable - NULL means system action |
| `actor_type` | varchar(20) | NOT NULL - `'platform_admin' \| 'system'` |
| `action` | varchar(80) | NOT NULL - e.g. `'invoice.marked_paid'`, `'subscription.overridden'`, `'tenant.auto_suspended_dunning'` |
| `entity_type` | varchar(40) | NOT NULL - `'invoice' \| 'subscription' \| 'gateway' \| 'tenant'` |
| `entity_id` | uuid | NOT NULL - PK of the affected row |
| `old_value` | jsonb | Nullable - previous state snapshot |
| `new_value` | jsonb | NOT NULL - new state snapshot |
| `reason` | text | NOT NULL for admin actions; system actions use fixed reason string |
| `created_at` | timestamptz | NOT NULL |

**Index:** `btree(tenant_id, created_at DESC)`, `btree(entity_type, entity_id)`, `btree(actor_id)`

**Constraint:** No triggers or application logic may UPDATE or DELETE rows in this table.
