# Infrastructure — Schema

**Module:** [[modules/infrastructure/overview|Infrastructure]]
**Phase:** Phase 1
**Tables:** 4

---

## `countries`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `name` | `varchar(100)` |  |
| `code` | `varchar(3)` | ISO 3166-1 alpha-3 |
| `phone_code` | `varchar(10)` |  |
| `currency_code` | `varchar(3)` |  |

---

## `file_records`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `file_name` | `varchar(255)` |  |
| `content_type` | `varchar(100)` | MIME type |
| `size_bytes` | `bigint` |  |
| `storage_path` | `varchar(500)` | Blob storage path |
| `uploaded_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[#`tenants`|tenants]], `uploaded_by_id` → [[#`users`|users]]

---

## `tenants`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `name` | `varchar(200)` | Company name |
| `slug` | `varchar(100)` | URL-safe identifier, UNIQUE |
| `industry_profile` | `varchar(30)` | `office_it`, `manufacturing`, `retail`, `healthcare`, `custom` — **sets monitoring defaults at signup** |
| `company_size_range` | `varchar(30)` | Employee-count range captured during Developer Platform provisioning, e.g. `1-50`, `51-200`, `201-500` |
| `status` | `varchar(20)` | `provisioning`, `trial`, `active`, `suspended`, `cancelled` |
| `subscription_plan_id` | `uuid` | FK → subscription_plans |
| `settings_json` | `jsonb` | Tenant-level settings |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `subscription_plan_id` → [[database/schemas/shared-platform#`subscription_plans`|subscription_plans]]

**Status semantics:**

- `provisioning` - Developer Platform draft tenant. Visible to `/admin/v1/*` operators, excluded from tenant-facing `/api/v1/*`, login, analytics, and normal customer workflows until activation.
- `trial` - Activated tenant in a time-limited trial/commercial evaluation state.
- `active` - Activated production tenant with tenant-facing access enabled.
- `suspended` - Temporarily disabled tenant. Data is preserved; tenant-facing login and workflows are blocked.
- `cancelled` - Commercially cancelled/offboarded tenant. Data retention, export, and purge follow the offboarding policy.

`company_size_range` is tenant profile metadata, not legal-entity data. Detailed provisioning progress is stored in `tenant_provisioning_states` and `tenant_provisioning_validation_results`; do not add wizard-step progress columns to `tenants`.

---

## `users`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `email` | `varchar(255)` | UNIQUE per tenant |
| `password_hash` | `varchar(255)` | BCrypt hash, work factor 12 |
| `first_name` | `varchar(100)` |  |
| `last_name` | `varchar(100)` |  |
| `is_active` | `boolean` |  |
| `email_verified` | `boolean` |  |
| `last_login_at` | `timestamptz` | Nullable |
| `must_change_password` | `boolean` | Set by Dev Platform admin when assigning a temporary password |
| `password_set_by_admin` | `boolean` | True when password was set via Dev Platform override |
| `temporary_password_expires_at` | `timestamptz` | Nullable — if set and in the past, login is blocked until admin resets |
| `password_reset_token_hash` | `varchar(128)` | Nullable — SHA-256 hex hash of the forgot-password reset token |
| `password_reset_token_expires_at` | `timestamptz` | Nullable — 1-hour expiry for password reset tokens |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` | Nullable |
| `is_deleted` | `boolean` | Soft delete |
| `created_by_id` | `uuid` | FK → users (who created this record) |

**Foreign Keys:** `tenant_id` → [[#`tenants`|tenants]]

---

## Related

- [[modules/infrastructure/overview|Infrastructure Module]]
- [[modules/auth/overview|Auth Module]] — authentication and token services use this table
- [[backend/api-conventions|API Conventions]] - first-party API auth and endpoint conventions
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]
