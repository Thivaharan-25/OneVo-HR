# Developer Platform Database Schema

## Overview

The OneVo Developer Platform introduces dedicated tables to manage platform accounts, platform roles and permissions, authentication sessions, agent version releases, and deployment ring assignments. This schema enables:

- **Multi-tenant admin isolation**: Developer platform accounts operate independently from tenant-facing systems
- **Permission-based platform RBAC**: Platform roles restrict access to Developer Platform modules and `/admin/v1/*` actions
- **Agent release management**: Semantic versioning, release channels (stable/beta/recalled), and OS compatibility tracking
- **Gradual rollout capabilities**: Deployment rings (Internal, Beta, GA) allow controlled agent version distribution across tenants
- **Session security**: OAuth-based authentication with token management and IP tracking
- **API access control**: Platform API key provisioning with scope-based permissions and expiration

**Phase 1** adds platform account/session/RBAC tables, release and ring management tables, plus the `global_app_catalog` table in the SharedPlatform schema managed by the App Catalog Manager module. **Phase 2** adds the `platform_api_keys` table for programmatic access.

---

## DbContext Ownership (ADR-001)

> **DbContext:** `ApplicationDbContext` in `ONEVO.Infrastructure/Persistence/`. DevPlatform entities (`DevPlatformAccount`, `DevPlatformSession`, `AgentVersionRelease`, `AgentDeploymentRing`, `AgentDeploymentRingAssignment`) are configured in `ONEVO.Infrastructure/Persistence/Configurations/DevPlatform/`. These entities have **no TenantId** and are excluded from the global tenant query filter.

Per [ADR-001](../../decisions/ADR-001-per-module-database-and-event-bus.md), all developer platform tables are mapped by the unified `ApplicationDbContext`. EF migrations live in `ONEVO.Infrastructure/Persistence/Migrations/` and are run as part of the standard application startup.

Cross-module data access (e.g., reading `tenants`) goes through the existing module's public service interface via DI â€” never by querying the DbContext directly across module boundaries.

---

## Schema Catalog Impact

| Phase | Change | Table Count |
|-------|--------|------------|
| Current | Baseline | 170 |
| Phase 1 | +5 DevPlatform tables + `global_app_catalog` (SharedPlatform) + `observed_applications` (Configuration) + 3 columns on `app_allowlists` | 177 |
| Phase 2 | +1 new table (`platform_api_keys`) | 178 |

> **Note on ownership:** `global_app_catalog` is owned by `SharedPlatformDbContext` and `observed_applications` by `ConfigurationDbContext`. They are not in `ApplicationDbContext`. The dev console manages them through `IGlobalAppCatalogService` and `IObservedApplicationReader` interfaces respectively.

---

## Phase 1 Tables

### dev_platform_accounts

Administrative accounts for the developer platform. Supports OAuth (Google Sign-In). Effective access is permission-based through account-role and role-permission mappings.

| Column | Type | Constraints / Notes |
|--------|------|-------------------|
| id | uuid | PRIMARY KEY |
| email | varchar(255) | UNIQUE, NOT NULL |
| full_name | varchar(255) | NOT NULL |
| google_sub | varchar(255) | Google OAuth subject identifier, nullable |
| legacy_role | varchar(30) | Nullable compatibility preset: `'super_admin'` \| `'admin'` \| `'viewer'`; do not use as the only authorization source |
| is_active | boolean | Default: true; controls login permission |
| created_at | timestamptz | NOT NULL; creation timestamp |
| last_login_at | timestamptz | Nullable; tracks last successful authentication |

**Indexes**: `UNIQUE(email)`, `btree(is_active)`

---

### dev_platform_account_invites

Pending invitations for platform managers.

| Column | Type | Constraints / Notes |
|--------|------|-------------------|
| id | uuid | PRIMARY KEY |
| email | varchar(255) | NOT NULL |
| full_name | varchar(255) | NOT NULL |
| invite_token_hash | varchar(64) | NOT NULL; raw token never stored |
| invited_by_id | uuid | FOREIGN KEY -> dev_platform_accounts(id), NOT NULL |
| expires_at | timestamptz | NOT NULL |
| accepted_at | timestamptz | Nullable |
| revoked_at | timestamptz | Nullable |
| created_at | timestamptz | NOT NULL |

---

### dev_platform_roles

Platform role presets and custom roles.

| Column | Type | Constraints / Notes |
|--------|------|-------------------|
| id | uuid | PRIMARY KEY |
| name | varchar(100) | NOT NULL |
| description | text | Nullable |
| is_system | boolean | System roles can be cloned but not deleted |
| is_active | boolean | Default true |
| created_by_id | uuid | FOREIGN KEY -> dev_platform_accounts(id), nullable for seed roles |
| created_at | timestamptz | NOT NULL |
| updated_at | timestamptz | NOT NULL |

---

### dev_platform_permissions

Catalog of platform-admin permissions. These control Developer Platform modules only; they are not tenant permissions.

| Column | Type | Constraints / Notes |
|--------|------|-------------------|
| code | varchar(120) | PRIMARY KEY, e.g. `platform.tenants.read` |
| module_key | varchar(80) | Developer Platform module key |
| description | text | Nullable |
| is_high_risk | boolean | Marks permissions such as impersonation and account management |

---

### dev_platform_role_permissions

Maps platform roles to platform permissions.

| Column | Type | Constraints / Notes |
|--------|------|-------------------|
| role_id | uuid | FOREIGN KEY -> dev_platform_roles(id), NOT NULL |
| permission_code | varchar(120) | FOREIGN KEY -> dev_platform_permissions(code), NOT NULL |
| granted_by_id | uuid | FOREIGN KEY -> dev_platform_accounts(id), NOT NULL |
| granted_at | timestamptz | NOT NULL |

**Primary key:** `(role_id, permission_code)`

---

### dev_platform_account_roles

Maps platform accounts to platform roles.

| Column | Type | Constraints / Notes |
|--------|------|-------------------|
| account_id | uuid | FOREIGN KEY -> dev_platform_accounts(id), NOT NULL |
| role_id | uuid | FOREIGN KEY -> dev_platform_roles(id), NOT NULL |
| assigned_by_id | uuid | FOREIGN KEY -> dev_platform_accounts(id), NOT NULL |
| assigned_at | timestamptz | NOT NULL |

**Primary key:** `(account_id, role_id)`

---

### dev_platform_sessions

Authenticated sessions for dev platform accounts. One session per login or API token grant.

| Column | Type | Constraints / Notes |
|--------|------|-------------------|
| id | uuid | PRIMARY KEY |
| account_id | uuid | FOREIGN KEY â†’ dev_platform_accounts(id), NOT NULL |
| token_hash | varchar(64) | SHA256 hash of session token, NOT NULL |
| created_at | timestamptz | NOT NULL |
| expires_at | timestamptz | NOT NULL; session TTL |
| ip_address | varchar(45) | Nullable; IPv4 or IPv6, for audit/security |

**Indexes**: `btree(account_id)`, `btree(expires_at)`

**Notes**: Tokens are hashed; original token never stored. Expired sessions are soft-deleted or archived for audit.

---

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
| published_by_id | uuid | FOREIGN KEY â†’ dev_platform_accounts(id), NOT NULL |
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
| tenant_id | uuid | FOREIGN KEY â†’ tenants(id), NOT NULL |
| ring_id | uuid | FOREIGN KEY â†’ agent_deployment_rings(id), NOT NULL |
| assigned_by_id | uuid | FOREIGN KEY â†’ dev_platform_accounts(id), NOT NULL |
| assigned_at | timestamptz | NOT NULL; assignment timestamp for audit |

**Indexes**: `UNIQUE(tenant_id, ring_id)`, `btree(ring_id)`, `btree(assigned_by_id)`

**Notes**: A tenant can belong to only one ring at a time (enforced by unique constraint). Ensures consistent version delivery within a ring cohort.

---

## Phase 2 Table

### platform_api_keys

API keys for programmatic access to the developer platform admin API. Supports revocation and expiration.

| Column | Type | Constraints / Notes |
|--------|------|-------------------|
| id | uuid | PRIMARY KEY |
| key_hash | varchar(64) | SHA256 hash of the API key, NOT NULL, UNIQUE |
| name | varchar(100) | NOT NULL; human-readable label for key management |
| scopes | text[] | Array of permission scopes; e.g., `ARRAY['agent:view-health', 'deployment:write']` |
| created_by_id | uuid | FOREIGN KEY â†’ dev_platform_accounts(id), NOT NULL |
| expires_at | timestamptz | Nullable; if set, key becomes invalid after this time |
| revoked_at | timestamptz | Nullable; if set, key is revoked and unusable |
| created_at | timestamptz | NOT NULL; key creation time |

**Indexes**: `UNIQUE(key_hash)`, `btree(created_by_id)`, `btree(expires_at)`, `btree(revoked_at)`

**Notes**: Keys are hashed on storage; original key is shown only once at creation. Revoked and expired keys are excluded from validation queries.

---

## Existing Table Changes

### tenants.status Enum

The canonical `tenants.status` lifecycle enum is: `provisioning`, `pending_confirmation`, `pending_payment`, `active`, `suspended`, and `cancelled`. Tenant creation does not create a trial. The Developer Platform uses `provisioning` for draft tenants while the wizard is incomplete; detailed wizard progress is stored in `tenant_provisioning_states` and `tenant_provisioning_validation_results`.

| Status | Meaning | Visibility |
|--------|---------|------------|
| `provisioning` | Onboarding draft in progress | Excluded from tenant-facing queries; visible only in admin API for platform managers |
| `pending_confirmation` | Tenant owner must confirm plan, billing cycle, employee count, and billing contact | Limited onboarding/billing confirmation access |
| `pending_payment` | First invoice generated and awaiting payment or manual approval | Limited billing/payment access |
| `active` | Production-ready tenant | Visible in all tenant-facing and admin queries |
| `suspended` | Temporarily disabled | Excluded from tenant-facing queries; visible only in admin API |
| `cancelled` | Commercially cancelled/offboarded tenant | Excluded from tenant-facing queries; visible in admin API for retention, export, and audit workflows |

**Visibility Rule**: Tenants in `provisioning` status are excluded from:
- Tenant-facing application queries
- Tenant-facing login/session creation
- Standard analytics and reporting

Provisioning tenants are visible to developer platform accounts with the required tenant permissions via `/admin/v1/*`, ensuring clean separation during onboarding workflows.

---

## Provisioning Activation Guard

`PATCH /admin/v1/tenants/{id}/provision/confirm` may activate a tenant only after the provisioning draft is complete. The guard requires:

- Completed tenant profile: company name, slug, primary contact email, country, industry profile, registration/profile name, registration number, estimated employee count, timezone, and currency.
- Persistence rule for tenant profile: country, registration/profile name, registration number, estimated employee count, timezone, currency, and contact metadata are stored as tenant profile/draft state. Tenant provisioning does not create `legal_entities` rows.
- Completed subscription/commercial terms: commercial model, plan or custom contract, billing cycle/currency, contract dates, gateway/manual billing mode, billing evidence for manual payment, payment exception/grace dates when approved, AI token limit when AI is included, Work Management storage limit when storage-backed Work Management is included, and maintenance status/renewal date when applicable.
- Completed module selection: active modules and each module's sales state are recorded through the entitlement registry.
- Completed role template application: at least the tenant owner/admin starter role is materialized from the module-filtered permission catalog. Role template completion is part of provisioning state, not optional decoration.
- Completed required settings/templates/setup services: monitoring defaults, privacy/transparency mode, leave defaults, template applications, setup-service state, and any module-required settings.
- Owner invite state is tracked separately. The invite email is sent only by the explicit invite action, not automatically by tenant creation, configuration, or activation. The same email can be invited to multiple isolated tenants.

Activation fails with `422 Unprocessable Entity` and a checklist of missing steps when any required item is incomplete. Provisioning tenants remain invisible to tenant-facing `/api/v1/*` APIs until activation succeeds.

---

## Security & Access Control

- **OAuth Integration**: dev_platform_accounts authenticate via Google OAuth; tokens are hashed in dev_platform_sessions
- **Permission-Based Access**: Platform roles map to explicit `dev_platform_permissions`; legacy role names are presets only
- **API Key Hashing**: platform_api_keys stores SHA256 hashes; plaintext keys never persisted
- **Audit Trail**: All admin actions (published_by_id, assigned_by_id, created_by_id) track who made changes
- **Tenant Isolation**: dev_platform_* tables are isolated from tenant_facing_* schema; cross-tenant queries are forbidden

---

## Cross-Module Tables Referenced by Developer Platform

The Developer Platform reads and writes many tables owned by existing ONEVO product modules via their service interfaces (never via direct DbContext cross-module access). These tables are defined in their owning module's schema but are documented here for completeness because the Developer Platform's admin API layer depends on them heavily.

**Source of truth:** `database/schema-catalog.md` for all ~288 tables. The canonical table definitions live in `database/schemas/` (one file per module). This section documents the shape of each table as the Developer Platform expects it.

---

### tenants (owned by: SharedPlatform)

Central tenant registry. One row per company onboarded to ONEVO.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `tenant_code` | varchar(30) | UNIQUE, NOT NULL â€” format `TEN-YYYYMMDD-XXXX` |
| `company_name` | varchar(100) | NOT NULL |
| `legal_company_name` | varchar(150) | NOT NULL |
| `domain` | varchar(255) | UNIQUE, NOT NULL â€” primary domain |
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
| `status` | varchar(20) | NOT NULL â€” see status enum above |
| `created_at` | timestamptz | NOT NULL |
| `created_by` | uuid | FK â†’ dev_platform_accounts(id) â€” the platform account that created the tenant |
| `activated_at` | timestamptz | Nullable â€” set when status transitions to active |
| `suspended_at` | timestamptz | Nullable |
| `cancelled_at` | timestamptz | Nullable |

**Indexes:** `UNIQUE(tenant_code)`, `UNIQUE(domain)`, `btree(status)`, `btree(created_at DESC)`

---

### tenant_provisioning_states (owned by: SharedPlatform)

Tracks 4-step wizard completion state. One row per tenant, created when the tenant row is created.

| Column | Type | Notes |
|---|---|---|
| `tenant_id` | uuid | PRIMARY KEY, FK â†’ tenants(id) |
| `step_1_complete` | boolean | NOT NULL, default false â€” Organization Info saved |
| `step_2_complete` | boolean | NOT NULL, default false â€” Admin Account set |
| `step_3_complete` | boolean | NOT NULL, default false â€” Subscription saved |
| `step_4_complete` | boolean | NOT NULL, default false â€” Configuration saved |
| `activated` | boolean | NOT NULL, default false â€” provision/confirm completed |
| `last_completed_step` | int | Nullable â€” 1â€“4, used to resume wizard at correct step |
| `updated_at` | timestamptz | NOT NULL |

---

### tenant_provisioning_validation_results (owned by: SharedPlatform)

Stores the most recent activation guard check results â€” the list of blocking items when `PATCH /provision/confirm` is attempted and fails.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `tenant_id` | uuid | FK â†’ tenants(id), NOT NULL |
| `checked_at` | timestamptz | NOT NULL â€” when the guard ran |
| `blockers` | jsonb | NOT NULL â€” array of `{code, message}` objects |
| `warnings` | jsonb | NOT NULL â€” array of `{code, message}` for non-blocking issues |
| `all_passed` | boolean | NOT NULL â€” true only when blockers is empty |

**Index:** `btree(tenant_id)`, `btree(checked_at DESC)`

---

### subscription_plans (owned by: SharedPlatform / Billing)

Global reusable plan catalog. Plans are not tenant-scoped.

| Column | Type | Notes |
|---|---|---|
| `id` | varchar(80) | PRIMARY KEY â€” human-readable slug e.g. `'plan-enterprise-2025-v1'` |
| `name` | varchar(80) | UNIQUE among active plans, NOT NULL |
| `tier` | varchar(30) | NOT NULL â€” `'enterprise' \| 'business' \| 'professional' \| 'custom'` |
| `description` | text | Nullable |
| `is_active` | boolean | NOT NULL, default true |
| `included_module_keys` | text[] | NOT NULL â€” array of module key strings |
| `included_feature_keys` | jsonb | NOT NULL, default `{}` â€” `{module_key: [feature_key...]}` commercial feature inclusion for partial module packages |
| `ai_capabilities` | boolean | NOT NULL, default false |
| `default_ai_monthly_token_limit` | bigint | Nullable â€” required when ai_capabilities = true |
| `work_management_storage` | boolean | NOT NULL, default false |
| `default_storage_limit_gb` | int | Nullable â€” required when work_management_storage = true |
| `supported_commercial_models` | text[] | NOT NULL â€” `['subscription', 'full_license_maintenance']` |
| `supported_billing_cycles` | text[] | Nullable â€” `['monthly', 'annual']` |
| `annual_discount_pct` | numeric(5,2) | Nullable â€” discount applied to monthly Ã— 12 for annual |
| `supported_collection_modes` | text[] | NOT NULL â€” `['gateway', 'manual']` |
| `created_by_id` | uuid | FK â†’ dev_platform_accounts(id) |
| `created_at` | timestamptz | NOT NULL |
| `updated_at` | timestamptz | NOT NULL |

---

### subscription_plan_price_brackets (owned by: SharedPlatform / Billing)

Employee-count pricing tiers per plan. Multiple rows per plan, one per employee-count tier.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `plan_id` | varchar(80) | FK â†’ subscription_plans(id), NOT NULL |
| `employee_count_tier` | varchar(20) | NOT NULL - e.g. `51-200` |
| `module_prices` | jsonb | NOT NULL â€” `{module_key: unit_price}` map |
| `calculated_monthly_total` | numeric(12,2) | NOT NULL - sum of selected module unit prices for this employee-count tier |
| `override_monthly_total` | numeric(12,2) | Nullable â€” operator-set flat total |
| `override_reason` | text | Nullable â€” required when override set |
| `currency` | varchar(3) | NOT NULL, ISO 4217 |
| `created_at` | timestamptz | NOT NULL |

**Unique constraint:** `(plan_id, employee_count_tier)`

---

### subscription_plan_price_history (owned by: SharedPlatform / Billing)

Immutable log of every price bracket change. Never updated, only inserted.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `plan_id` | varchar(80) | FK â†’ subscription_plans(id), NOT NULL |
| `employee_count_tier` | varchar(20) | NOT NULL |
| `module_key` | varchar(80) | NOT NULL â€” which module's price changed |
| `previous_unit_price` | numeric(12,2) | NOT NULL |
| `new_unit_price` | numeric(12,2) | NOT NULL |
| `changed_by_id` | uuid | FK â†’ dev_platform_accounts(id), NOT NULL |
| `changed_at` | timestamptz | NOT NULL |
| `reason` | text | Nullable |

---

### tenant_subscriptions (owned by: SharedPlatform / Billing)

Commercial snapshot per tenant. One active row per tenant. Immutable snapshot of the terms at assignment â€” changes create a new row and archive the old one.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `tenant_id` | uuid | FK â†’ tenants(id), NOT NULL |
| `plan_id` | varchar(80) | FK â†’ subscription_plans(id), NOT NULL |
| `is_current` | boolean | NOT NULL â€” only one true per tenant |
| `commercial_model` | varchar(30) | NOT NULL â€” `'subscription' \| 'full_license_maintenance'` |
| `billing_cycle` | varchar(10) | `'monthly' \| 'annual'` â€” null for full_license |
| `billing_start_date` | date | NOT NULL |
| `next_billing_date` | date | Nullable â€” calculated from billing_start + cycle |
| `billing_end_date` | date | Nullable â€” when contract ends |
| `collection_mode` | varchar(20) | NOT NULL â€” `'gateway' \| 'manual'` |
| `payment_gateway_id` | varchar(80) | FK â†’ payment_gateway_configs(id) â€” nullable when manual |
| `selected_module_keys` | text[] | NOT NULL â€” snapshot of modules at assignment time |
| `selected_feature_keys` | jsonb | NOT NULL, default `{}` â€” snapshot of included commercial feature keys at assignment time |
| `estimated_employee_count` | int | Nullable operator-entered estimate; not final invoice quantity |
| `calculated_price` | numeric(12,2) | NOT NULL â€” price from brackets at assignment time |
| `override_price` | numeric(12,2) | Nullable |
| `override_reason` | text | Nullable â€” required when override set |
| `effective_price` | numeric(12,2) | NOT NULL â€” `COALESCE(override_price, calculated_price)` |
| `currency` | varchar(3) | NOT NULL |
| `ai_monthly_token_limit` | bigint | Nullable |
| `work_management_storage_limit_gb` | int | Nullable |
| `payment_status` | varchar(20) | NOT NULL â€” `'current' \| 'overdue' \| 'grace_period' \| 'excepted'` |
| `payment_exception_start` | date | Nullable |
| `payment_exception_end` | date | Nullable |
| `payment_exception_reason` | text | Nullable |
| `billing_evidence_file_id` | uuid | Nullable â€” for manual collection |
| `billing_evidence_reference` | varchar(200) | Nullable â€” external reference for manual collection |
| `full_license_amount` | numeric(12,2) | Nullable â€” for full_license_maintenance |
| `maintenance_rate_pct` | numeric(5,2) | Nullable |
| `maintenance_collection_mode` | varchar(20) | Nullable â€” `'gateway' \| 'manual' \| 'waived'` |
| `maintenance_renewal_date` | date | Nullable |
| `maintenance_status` | varchar(20) | Nullable â€” `'current' \| 'overdue' \| 'waived'` |
| `payment_attempt_count` | int | NOT NULL, default 0 â€” dunning retry counter |
| `assigned_by_id` | uuid | FK â†’ dev_platform_accounts(id), NOT NULL |
| `assigned_at` | timestamptz | NOT NULL |
| `archived_at` | timestamptz | Nullable â€” set when superseded by new row |

**Index:** `btree(tenant_id, is_current)`, `btree(next_billing_date)`, `btree(payment_status)`

---

### module_catalog (owned by: SharedPlatform)

Global ONEVO product module registry. One row per module. Managed by Module Catalog Manager.

| Column | Type | Notes |
|---|---|---|
| `module_key` | varchar(80) | PRIMARY KEY â€” e.g. `'leave'`, `'activity_monitoring'` |
| `name` | varchar(100) | NOT NULL â€” display name |
| `description` | text | Nullable |
| `pillar` | varchar(30) | NOT NULL â€” `'hr_management' \| 'workforce_intelligence' \| 'worksync' \| 'shared'` |
| `pricing_unit` | varchar(30) | NOT NULL â€” `'per_employee' \| 'per_device' \| 'per_user' \| 'per_seat' \| 'flat' \| 'per_event'` |
| `is_sellable` | boolean | NOT NULL â€” false for always-included modules like notifications |
| `is_active` | boolean | NOT NULL â€” false hides from catalog and provisioning |
| `phase` | int | NOT NULL â€” 1 = Phase 1, 2 = Phase 2 |
| `setup_service_keys` | text[] | Nullable â€” connected setup service keys |
| `has_ai_capability` | boolean | NOT NULL, default false |
| `requires_storage` | boolean | NOT NULL, default false |
| `created_at` | timestamptz | NOT NULL |
| `updated_at` | timestamptz | NOT NULL |

---

### module_features (owned by: SharedPlatform)

Commercial feature registry inside a module. These rows define what can be included in plans or tenant-specific custom contracts. They are not runtime rollout flags.

| Column | Type | Notes |
|---|---|---|
| `feature_key` | varchar(120) | PRIMARY KEY â€” format `{module_key}.{feature_name}` |
| `module_key` | varchar(80) | FK â†’ module_catalog(module_key), NOT NULL |
| `name` | varchar(100) | NOT NULL |
| `description` | text | Nullable |
| `is_default_included` | boolean | NOT NULL, default true â€” selected by default when the module is added to a plan |
| `is_active` | boolean | NOT NULL, default true |
| `created_at` | timestamptz | NOT NULL |
| `updated_at` | timestamptz | NOT NULL |

**Index:** `btree(module_key, is_active)`

---

### module_permission_ownership (owned by: SharedPlatform)

Exclusive ownership map between product modules and seeded tenant-facing permission codes. This table is the authority for filtering tenant role builders by active module entitlement. Permission namespaces do not need to match `module_catalog.module_key`; for example, `core_hr` can own `employees:read` and `employees:write`.

| Column | Type | Notes |
|---|---|---|
| `module_key` | varchar(80) | FK â†’ module_catalog(module_key), NOT NULL |
| `permission_code` | varchar(120) | FK â†’ platform_permission_catalog(code), NOT NULL |
| `is_default_permission` | boolean | NOT NULL, default false â€” included in the tenant Owner role during future tenant activation |
| `created_at` | timestamptz | NOT NULL |
| `updated_at` | timestamptz | NOT NULL |

**Primary key:** `(module_key, permission_code)`

**Unique constraint:** `(permission_code)` â€” a permission can be owned by only one module.

**Rule:** Permission codes are seeded/version-controlled. Module Catalog assigns ownership of existing permission codes; it does not create or rename permission codes.

---

### platform_permission_catalog (owned by: SharedPlatform)

Master registry of all ONEVO tenant-facing permission codes. This is the authoritative list that the permission picker reads â€” it includes every permission that exists in the system, whether claimed by a module or unclaimed. Without this table, unclaimed permissions would have no home and the `/available` endpoint could only return already-claimed ones.

This table is distinct from `dev_platform_permissions`, which lists developer platform admin permissions (e.g. `platform.tenants.read`). This table lists tenant-facing permissions (e.g. `leave:approve`, `core_hr:read`).

| Column | Type | Notes |
|---|---|---|
| `code` | varchar(120) | PRIMARY KEY â€” e.g. `'leave:approve'`, `'core_hr:read'` |
| `display_name` | varchar(150) | NOT NULL â€” human-readable label shown in permission picker |
| `description` | text | Nullable â€” explains what granting this permission allows |
| `is_high_risk` | boolean | NOT NULL, default false â€” flagged permissions shown with warning in role builders |
| `created_at` | timestamptz | NOT NULL |

**Index:** `btree(code)`

**How `GET /admin/v1/modules/catalog/{moduleKey}/permissions/available` uses this table:**

```sql
SELECT
  p.code,
  p.display_name,
  p.description,
  p.is_high_risk,
  owned_module.module_key AS owned_by_module_key,
  owned_module.name       AS owned_by_module_name
FROM platform_permission_catalog p
LEFT JOIN module_permission_ownership mpo
  ON mpo.permission_code = p.code
LEFT JOIN module_catalog owned_module
  ON owned_module.module_key = mpo.module_key
ORDER BY p.code;
```

The frontend uses `owned_by_module_key` to determine picker state:
- `null` â†’ unclaimed â€” checkbox enabled
- equals current module key â†’ already owned by this module â€” checked
- any other value â†’ owned by another module â€” checkbox disabled, tooltip shows `owned_by_module_name`

**Seeding:** Permission codes are seeded by backend permission migrations/seeders. Module ownership rows are seeded separately in `module_permission_ownership`. New permission codes added by backend changes must have a corresponding `platform_permission_catalog` row before they can be assigned to a module.

---

### module_catalog_price_history (owned by: SharedPlatform)

Immutable price change audit trail for the module catalog. One row written per `PATCH /admin/v1/modules/catalog/{moduleKey}/pricing` call. Never updated or deleted.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `module_key` | varchar(80) | FK â†’ module_catalog(module_key), NOT NULL |
| `changed_by_id` | uuid | FK â†’ dev_platform_accounts(id), NOT NULL |
| `changed_at` | timestamptz | NOT NULL |
| `previous_price_brackets` | jsonb | NOT NULL â€” full bracket snapshot before the change |
| `new_price_brackets` | jsonb | NOT NULL â€” full bracket snapshot after the change |
| `reason` | text | Nullable â€” operator-provided reason for the change |

**Indexes:** `btree(module_key, changed_at DESC)`

**Notes:** Append-only. Tracks module base pricing changes only â€” `subscription_plan_price_history` separately tracks plan-level pricing snapshots.

---

### tenant_module_entitlements (owned by: SharedPlatform)

Runtime access source of truth. One row per module per tenant. This table â€” not the subscription snapshot â€” is what the ONEVO application checks to determine if a tenant may access a module.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `tenant_id` | uuid | FK â†’ tenants(id), NOT NULL |
| `module_key` | varchar(80) | FK â†’ module_catalog(module_key), NOT NULL |
| `status` | varchar(30) | NOT NULL â€” see entitlement status enum |
| `sales_state` | varchar(30) | NOT NULL â€” see sales state enum |
| `runtime_override` | boolean | Nullable runtime-only override; `NULL` inherits commercial entitlement, `false` force-disables runtime access, `true` explicitly restores runtime access without bypassing commercial entitlement |
| `unit_price` | numeric(12,2) | Nullable â€” module-specific override price |
| `currency` | varchar(3) | Nullable |
| `start_date` | date | Nullable |
| `end_date` | date | Nullable - subscription or entitlement end |
| entitlement_source | varchar(30) | NOT NULL - 'plan_included' | 'add_on' | 'operator_grant' |
| `assigned_by_id` | uuid | FK â†’ dev_platform_accounts(id), NOT NULL |
| `assigned_at` | timestamptz | NOT NULL |
| `updated_at` | timestamptz | NOT NULL |

**Unique constraint:** `(tenant_id, module_key)`
**Index:** `btree(tenant_id, status)` â€” queried on every permission resolution
**Runtime rule:** Module runtime access requires an active commercial entitlement and `runtime_override IS DISTINCT FROM false`. A `true` override does not grant access when the module is not commercially entitled.

**Entitlement status enum:**
| Value | Meaning |
|---|---|
| `provisioning` | Set during wizard â€” not yet active; tenant cannot access module |
| `active` | Tenant has runtime access |
| `suspended` | Access paused (e.g. payment failure) |
| `disabled` | Explicitly turned off â€” not accessible |

**Sales state enum:**
| Value | Meaning |
|---|---|
| `subscription_included` | Part of the subscription plan |
| `purchased` | Full license purchased |
| `maintenance_included` | Included in maintenance contract |
| `quoted` | Quoted to customer â€” not yet purchased; no access |
| `available` | In catalog, can be purchased â€” not yet active; no access |
| `disabled` | Not accessible and not in sales pipeline |

---

### payment_gateway_configs (owned by: SharedPlatform / Billing)

Encrypted payment gateway configurations. Secrets are AES-256 encrypted and never returned by API.

| Column | Type | Notes |
|---|---|---|
| `id` | varchar(80) | PRIMARY KEY â€” e.g. `'gw-paddle-global-prod'` |
| `provider` | varchar(20) | NOT NULL - `stripe`, `paddle`, or `payhere` |
| `name` | varchar(80) | NOT NULL |
| `logo_url` | varchar(500) | Nullable â€” uploaded via `POST /admin/v1/uploads/gateway-logo`; shown in gateway selection dropdown during tenant provisioning Step 3 and in Subscription Manager |
| `country_codes` | text[] | NOT NULL â€” applicable countries |
| `environment` | varchar(20) | NOT NULL â€” `'sandbox' \| 'production'` |
| `config_encrypted` | text | NOT NULL â€” AES-256 JSON blob (never returned by API) |
| `is_active` | boolean | NOT NULL, default true |
| `created_by_id` | uuid | FK â†’ dev_platform_accounts(id), NOT NULL |
| `created_at` | timestamptz | NOT NULL |
| `updated_at` | timestamptz | NOT NULL |

**Payload inside `config_encrypted` (Stripe):** `secret_key`, `publishable_key`, `webhook_secret`
**Payload inside `config_encrypted` (Paddle):** `api_key`, `seller_id`, `webhook_secret`
**Payload inside `config_encrypted` (PayHere):** `merchant_id`, `merchant_secret`, `webhook_secret`

---

### subscription_invoices (owned by: SharedPlatform / Billing)

Invoice records for all tenant billing cycles.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `invoice_number` | varchar(50) | UNIQUE, NOT NULL â€” format `INV-{tenant_code}-{YYYYMM}-{seq}` |
| `tenant_id` | uuid | FK â†’ tenants(id), NOT NULL |
| `subscription_id` | uuid | FK â†’ tenant_subscriptions(id), NOT NULL |
| `billing_period_start` | date | NOT NULL |
| `billing_period_end` | date | NOT NULL |
| `line_items` | jsonb | NOT NULL â€” array of `{module_key, name, unit_price, quantity, pricing_unit, line_total}` |
| `subtotal` | numeric(12,2) | NOT NULL |
| `calculated_price` | numeric(12,2) | NOT NULL |
| `override_price` | numeric(12,2) | Nullable |
| `effective_price` | numeric(12,2) | NOT NULL |
| `tax_amount` | numeric(12,2) | NOT NULL, default 0 |
| `total` | numeric(12,2) | NOT NULL |
| `currency` | varchar(3) | NOT NULL |
| `status` | varchar(20) | NOT NULL â€” `'draft' \| 'open' \| 'paid' \| 'overdue' \| 'void' \| 'uncollectible' \| 'partially_refunded'` |
| `due_date` | date | NOT NULL |
| `payment_method` | varchar(20) | Nullable - `stripe`, `paddle`, `payhere`, `manual`, or `waived` |
| `payment_reference` | varchar(200) | Nullable â€” external bank ref or gateway charge ID |
| `paddle_transaction_id` | varchar(100) | Nullable â€” idempotency key for Paddle transactions |
| `paddle_invoice_url` | varchar(500) | Nullable â€” Paddle-hosted invoice PDF URL |
| `gateway_charge_id` | varchar(100) | Nullable â€” PayHere charge ref |
| `payment_attempt_count` | int | NOT NULL, default 0 â€” incremented per gateway retry |
| `created_at` | timestamptz | NOT NULL |
| `updated_at` | timestamptz | NOT NULL |

**Index:** `btree(tenant_id, status)`, `btree(due_date)`, `btree(paddle_transaction_id)`, `UNIQUE(invoice_number)`

---

### webhook_event_queue (owned by: SharedPlatform / Billing)
Reliable event processing queue for inbound Stripe, Paddle, and PayHere webhooks. Ensures at-least-once processing with dead-letter tracking.

| Column | Type | Notes |
|---|---|---|
| `provider` | varchar(20) | NOT NULL - `stripe`, `paddle`, or `payhere` |
| `event_id` | varchar(100) | UNIQUE, NOT NULL - provider event/order ID; idempotency key |
| `event_type` | varchar(100) | NOT NULL â€” e.g. `'payment_intent.succeeded'` |
| `payload` | jsonb | NOT NULL â€” full webhook payload |
| `status` | varchar(20) | NOT NULL â€” `'pending' \| 'processing' \| 'completed' \| 'failed' \| 'dead_letter'` |
| `attempt_count` | int | NOT NULL, default 0 |
| `last_attempt_at` | timestamptz | Nullable |
| `next_retry_at` | timestamptz | Nullable â€” exponential backoff schedule |
| `error_message` | text | Nullable â€” last processing error |
| `received_at` | timestamptz | NOT NULL |
| `completed_at` | timestamptz | Nullable |

**Index:** `btree(status, next_retry_at)`, `UNIQUE(provider, event_id)`

---

### platform_alerts (owned by: DevPlatform)

Cross-tenant operational alerts. Owned by the DevPlatform feature namespace, not by product module teams. The Developer Platform creates, manages, and resolves these alerts.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `alert_code` | varchar(80) | NOT NULL â€” machine-readable code from the alert catalog |
| `severity` | varchar(10) | NOT NULL â€” `'critical' \| 'warning' \| 'info'` |
| `tenant_id` | uuid | Nullable, FK â†’ tenants(id) â€” null for platform-level alerts |
| `source_module` | varchar(80) | NOT NULL â€” module key that raised the alert |
| `title` | varchar(200) | NOT NULL â€” human-readable summary |
| `detail` | text | Nullable â€” additional context (IPs, counts, thresholds, etc.) |
| `created_at` | timestamptz | NOT NULL |
| `auto_resolved` | boolean | NOT NULL, default false |
| `resolved_at` | timestamptz | Nullable |
| `resolved_by_id` | uuid | Nullable, FK â†’ dev_platform_accounts(id) |
| `resolved_reason` | text | Nullable â€” required for Critical severity |
| `acknowledged_at` | timestamptz | Nullable |
| `acknowledged_by_id` | uuid | Nullable, FK â†’ dev_platform_accounts(id) |
| `auto_dismissed` | boolean | NOT NULL, default false â€” Info alerts dismissed after 48h |

**Index:** `btree(severity, created_at DESC)`, `btree(tenant_id, severity)`, `btree(alert_code)`, partial index on `(resolved_at IS NULL)` for active alert queries

---

### feature_flags (owned by: Configuration)

Global feature flag definitions. Managed by Feature Flag Manager.

| Column | Type | Notes |
|---|---|---|
| `key` | varchar(120) | PRIMARY KEY |
| `description` | text | Nullable |
| `default_value` | boolean | NOT NULL |
| `rollout_percentage` | int | NOT NULL, 0â€“100 â€” % of tenants that get this flag as ON globally |
| `module_key` | varchar(80) | Nullable FK â†’ module_catalog(module_key) â€” which module this flag gates |
| `feature_key` | varchar(120) | Nullable FK â†’ module_features(feature_key) â€” commercial feature this flag controls at runtime |
| `is_active` | boolean | NOT NULL, default true |
| `created_at` | timestamptz | NOT NULL |
| `updated_at` | timestamptz | NOT NULL |

**Linkage rule:** Tenant-facing product feature flags must set both `module_key` and `feature_key`, and `feature_key` must reference a feature owned by that module in `module_features`. Only platform operational flags that are not sold as tenant features may leave `module_key` and `feature_key` null.

---

### feature_flag_overrides (owned by: Configuration)

Per-tenant feature flag overrides. Overrides the global default for a specific tenant after commercial entitlement and feature inclusion pass.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `flag_key` | varchar(120) | FK â†’ feature_flags(key), NOT NULL |
| `tenant_id` | uuid | FK â†’ tenants(id), NOT NULL |
| `value` | boolean | NOT NULL â€” the overridden value for this tenant |
| `granted_by_id` | uuid | FK â†’ dev_platform_accounts(id), NOT NULL |
| `granted_at` | timestamptz | NOT NULL |
| `reason` | text | Nullable |

**Unique constraint:** `(flag_key, tenant_id)`

---

### users (owned by: Auth â€” shown here for cross-reference)

Tenant-scoped user accounts. Every user belongs to exactly one tenant. **Admin-invited users** have `status = 'invited'` until they complete set-password via invite link.

Key columns relevant to Developer Platform operations:

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `tenant_id` | uuid | FK â†’ tenants(id), NOT NULL â€” always tenant-scoped |
| `email` | varchar(255) | NOT NULL |
| `first_name` | varchar(50) | NOT NULL |
| `last_name` | varchar(50) | NOT NULL |
| `status` | varchar(20) | `'invited' \| 'active' \| 'suspended' \| 'deactivated'` |
| `role_label` | varchar(80) | Label from provisioning â€” actual permissions from roles/role_permissions |
| `work_mode` | varchar(20) | `'hybrid' \| 'remote' \| 'on_site'` |
| `invite_sent_at` | timestamptz | Nullable |
| `invite_expires_at` | timestamptz | Nullable â€” 72 hours from invite_sent_at |
| `send_invite_on_activation` | boolean | NOT NULL, default true |
| `last_login_at` | timestamptz | Nullable |
| `created_at` | timestamptz | NOT NULL |

**Multi-tenant email rule:** Same email can exist in `users` across multiple tenants with different `tenant_id`. This is enforced at application layer â€” each user+tenant pair is independent.

---

---

## Integration & AI Provider Tables

### ai_provider_configs (owned by: DevPlatform)

Global AI provider configuration per purpose. One row per ONEVO AI feature purpose (agentic_chat, ai_insights, report_generation). No hardcoded provider names or model names â€” all operator-configured.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `config_name` | varchar(80) | NOT NULL â€” operator-chosen label |
| `logo_url` | varchar(500) | Nullable â€” uploaded via `POST /admin/v1/uploads/ai-provider-logo` |
| `purpose` | varchar(40) | UNIQUE NOT NULL â€” `'agentic_chat' \| 'ai_insights' \| 'report_generation'` |
| `provider_format` | varchar(30) | NOT NULL â€” `'openai_compatible' \| 'anthropic'` â€” API request/response shape only |
| `api_base_url` | varchar(500) | NOT NULL â€” always required; no default |
| `model` | varchar(120) | NOT NULL â€” set from provider's model fetch, not typed free-form |
| `api_key_encrypted` | text | NOT NULL â€” AES-256; never returned by API |
| `request_timeout_seconds` | int | NOT NULL, default 60 |
| `max_retries` | int | NOT NULL, default 2 |
| `is_active` | boolean | NOT NULL, default true |
| `last_verified_at` | timestamptz | Nullable |
| `last_verification_status` | varchar(20) | Nullable â€” `'healthy' \| 'error'` |
| `updated_by_id` | uuid | FK â†’ dev_platform_accounts(id) |
| `updated_at` | timestamptz | NOT NULL |

**Index:** `UNIQUE(purpose)`

---

### tenant_ai_provider_overrides (owned by: DevPlatform)

Per-tenant AI config overrides. One row per (tenant, purpose) pair. When present and active, takes precedence over global `ai_provider_configs` for that tenant.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `tenant_id` | uuid | FK â†’ tenants(id), NOT NULL |
| `purpose` | varchar(40) | NOT NULL |
| `config_name` | varchar(80) | NOT NULL |
| `provider_format` | varchar(30) | NOT NULL |
| `api_base_url` | varchar(500) | NOT NULL |
| `model` | varchar(120) | NOT NULL |
| `api_key_encrypted` | text | NOT NULL â€” AES-256 |
| `request_timeout_seconds` | int | NOT NULL |
| `max_retries` | int | NOT NULL |
| `is_active` | boolean | NOT NULL, default true |
| `set_by_id` | uuid | FK â†’ dev_platform_accounts(id), NOT NULL |
| `set_at` | timestamptz | NOT NULL |

**Unique:** `(tenant_id, purpose)`

---

### platform_oauth_apps (owned by: DevPlatform)

ONEVO's OAuth app registrations used when tenants connect Customer OAuth integrations. One row per provider. These are ONEVO's developer credentials â€” not the tenant's tokens.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `provider` | varchar(30) | UNIQUE NOT NULL â€” operator-set slug, e.g. `'github'`, `'microsoft'`, `'google'`, `'slack'` |
| `app_name` | varchar(100) | NOT NULL â€” shown in OAuth consent screen |
| `logo_url` | varchar(500) | Nullable â€” uploaded via `POST /admin/v1/uploads/oauth-app-logo`; stored in platform file storage |
| `client_id` | varchar(200) | NOT NULL â€” not encrypted; used in redirect URLs |
| `client_secret_encrypted` | text | NOT NULL â€” AES-256 |
| `additional_config_encrypted` | text | Nullable â€” GitHub App private key and other provider extras |
| `authorization_url` | varchar(500) | NOT NULL |
| `token_url` | varchar(500) | NOT NULL |
| `default_scopes` | text[] | NOT NULL |
| `is_active` | boolean | NOT NULL |
| `last_verified_at` | timestamptz | Nullable |
| `updated_by_id` | uuid | FK â†’ dev_platform_accounts(id) |
| `updated_at` | timestamptz | NOT NULL |

**Index:** `UNIQUE(provider)`

---

### platform_service_keys (owned by: DevPlatform)

ONEVO's own third-party service API keys used internally across all tenants (Resend, Cloudflare, etc.).

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `service_key` | varchar(50) | UNIQUE NOT NULL â€” e.g. `'resend'`, `'cloudflare'`, `'azure_blob'` |
| `display_name` | varchar(80) | NOT NULL |
| `api_key_encrypted` | text | NOT NULL â€” AES-256 |
| `is_active` | boolean | NOT NULL |
| `last_verified_at` | timestamptz | Nullable |
| `updated_by_id` | uuid | FK â†’ dev_platform_accounts(id) |
| `updated_at` | timestamptz | NOT NULL |

**Index:** `UNIQUE(service_key)`

---

### integration_catalog (owned by: SharedPlatform)

Operator-managed catalog of all integrations tenants can connect. Fully dynamic â€” operators create entries here, nothing is hardcoded in the ONEVO application.

| Column | Type | Notes |
|---|---|---|
| `integration_key` | varchar(50) | PRIMARY KEY â€” operator-set slug, e.g. `'github'`, `'ms_teams'` |
| `display_name` | varchar(100) | NOT NULL |
| `description` | text | Nullable |
| `category` | varchar(30) | NOT NULL â€” `'customer_oauth' \| 'platform_managed'` |
| `auth_type` | varchar(30) | NOT NULL â€” `'oauth2' \| 'api_key' \| 'webhook' \| 'saml' \| 'platform_managed'` |
| `oauth_app_provider` | varchar(30) | Nullable FK â†’ platform_oauth_apps(provider) â€” which ONEVO OAuth app handles the OAuth flow |
| `show_in_module_config` | boolean | NOT NULL, default true â€” whether shown in Module Catalog Manager's Integrations tab |
| `logo_url` | varchar(500) | Nullable |
| `is_active` | boolean | NOT NULL, default true |
| `created_by_id` | uuid | FK â†’ dev_platform_accounts(id) |
| `created_at` | timestamptz | NOT NULL |

---

### module_integration_links (owned by: SharedPlatform)

Links ONEVO product modules to integration catalog entries. Managed through Module Catalog Manager â†’ module detail â†’ Integrations tab.

| Column | Type | Notes |
|---|---|---|
| `module_key` | varchar(80) | FK â†’ module_catalog(module_key), NOT NULL |
| `integration_key` | varchar(50) | FK â†’ integration_catalog(integration_key), NOT NULL |
| `link_type` | varchar(20) | NOT NULL â€” `'required'` |
| `linked_by_id` | uuid | FK â†’ dev_platform_accounts(id), NOT NULL |
| `linked_at` | timestamptz | NOT NULL |

**Primary key:** `(module_key, integration_key)`
**Read as:** "When a tenant is entitled to `module_key`, integration `integration_key` becomes available to them."

---

### tenant_integration_credentials (owned by: Auth / SharedPlatform)

Stores per-tenant OAuth tokens and connection state for Customer OAuth integrations. Written when a tenant's user completes the OAuth flow. Read by the main ONEVO app to call integration APIs on behalf of the tenant.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `tenant_id` | uuid | FK â†’ tenants(id), NOT NULL |
| `integration_key` | varchar(50) | FK â†’ integration_catalog(integration_key), NOT NULL |
| `access_token_encrypted` | text | Nullable â€” AES-256; refreshed automatically before expiry |
| `refresh_token_encrypted` | text | Nullable â€” AES-256 |
| `token_expires_at` | timestamptz | Nullable |
| `scopes_granted` | text[] | Scopes the customer actually authorised during OAuth |
| `external_account_id` | varchar(200) | Nullable â€” GitHub org ID, Microsoft tenant ID, Google workspace ID, etc. |
| `external_account_name` | varchar(200) | Nullable â€” human-readable name of the connected account |
| `status` | varchar(20) | NOT NULL â€” `'connected' \| 'error' \| 'expired' \| 'disconnected'` |
| `last_sync_at` | timestamptz | Nullable |
| `error_message` | text | Nullable â€” last error from provider |
| `connected_at` | timestamptz | NOT NULL |
| `connected_by_user_id` | uuid | FK â†’ users(id) â€” which tenant user completed the OAuth |
| `disconnected_at` | timestamptz | Nullable |

**Unique:** `(tenant_id, integration_key)` â€” one connection per integration per tenant
**Index:** `btree(tenant_id, status)`, `btree(integration_key)`

---

## Schema Impact Summary (Updated)

| Phase | New Tables Added | Running Total |
|---|---|---|
| Baseline | â€” | 170 |
| DevPlatform Phase 1 | `dev_platform_accounts`, `dev_platform_account_invites`, `dev_platform_roles`, `dev_platform_permissions`, `dev_platform_role_permissions`, `dev_platform_account_roles`, `dev_platform_sessions`, `agent_version_releases`, `agent_deployment_rings`, `agent_deployment_ring_assignments`, `platform_alerts`, `webhook_event_queue` | 182 |
| DevPlatform Phase 2 | `platform_api_keys` | 183 |
| Cross-module additions | `tenant_provisioning_states`, `tenant_provisioning_validation_results` | 185 |
| AI / Gateway / Integration | `ai_provider_configs`, `tenant_ai_provider_overrides`, `platform_oauth_apps`, `platform_service_keys`, `integration_catalog`, `module_integration_links`, `tenant_integration_credentials` | 192 |
| Billing additions | `billing_audit_logs` | 193 |
| Permission catalog | `platform_permission_catalog` | 194 |

**Note:** `subscription_plans`, `subscription_plan_price_brackets`, `subscription_plan_price_history`, `tenant_subscriptions`, `tenant_module_entitlements`, `module_catalog`, `payment_gateway_configs`, `subscription_invoices`, `feature_flags`, `feature_flag_overrides`, `feature_access_grants`, `users` are existing SharedPlatform/Auth/Billing tables. Authoritative definitions in `database/schemas/shared-platform.sql` and `database/schemas/auth.sql`.

---

### billing_audit_logs (owned by: SharedPlatform / Billing)

Immutable append-only audit trail for all billing mutations. No UPDATE or DELETE permitted on this table.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PRIMARY KEY |
| `tenant_id` | uuid | FK â†’ tenants(id), NOT NULL |
| `actor_id` | uuid | FK â†’ dev_platform_accounts(id), Nullable â€” NULL means system action |
| `actor_type` | varchar(20) | NOT NULL â€” `'platform_admin' \| 'system'` |
| `action` | varchar(80) | NOT NULL â€” e.g. `'invoice.marked_paid'`, `'subscription.overridden'`, `'tenant.auto_suspended_dunning'` |
| `entity_type` | varchar(40) | NOT NULL â€” `'invoice' \| 'subscription' \| 'gateway' \| 'tenant'` |
| `entity_id` | uuid | NOT NULL â€” PK of the affected row |
| `old_value` | jsonb | Nullable â€” previous state snapshot |
| `new_value` | jsonb | NOT NULL â€” new state snapshot |
| `reason` | text | NOT NULL for admin actions; system actions use fixed reason string |
| `created_at` | timestamptz | NOT NULL |

**Index:** `btree(tenant_id, created_at DESC)`, `btree(entity_type, entity_id)`, `btree(actor_id)`

**Constraint:** No triggers or application logic may UPDATE or DELETE rows in this table.

