# Infrastructure - Schema

**Module:** [[modules/infrastructure/overview|Infrastructure]]
**Phase:** Phase 1
**Tables:** 5

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
| `tenant_id` | `uuid` | FK -> tenants |
| `file_name` | `varchar(255)` |  |
| `content_type` | `varchar(100)` | MIME type |
| `size_bytes` | `bigint` |  |
| `storage_path` | `varchar(500)` | Blob storage path |
| `uploaded_by_id` | `uuid` | FK -> users |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[#`tenants`|tenants]], `uploaded_by_id` -> [[#`users`|users]]

---

## `entity_assets`

Generic links from normal product entities to files. Use this table for reusable display assets and ordinary attachments only. Do not use it for monitoring screenshots, identity verification camera photos, clock-in/out photos, or other evidence/compliance files.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants; nullable only for platform-level assets such as platform user avatars |
| `owner_type` | `varchar(50)` | Backend-owned discriminator, e.g. `tenant_user`, `platform_user`, `tenant`, `project`, `company`, `support_ticket`, `support_ticket_message`, `document` |
| `owner_id` | `uuid` | ID of the owning entity |
| `asset_purpose` | `varchar(50)` | Backend-owned purpose, e.g. `profile_photo`, `avatar`, `company_logo`, `tenant_logo`, `project_cover`, `attachment` |
| `file_record_id` | `uuid` | FK -> file_records |
| `is_primary` | `boolean` | Primary asset for the owner + purpose |
| `sort_order` | `integer` | Optional display ordering for attachments |
| `metadata` | `jsonb` | Safe non-secret metadata |
| `created_by_type` | `varchar(30)` | `user` or `platform_user` |
| `created_by_id` | `uuid` | Actor ID matching `created_by_type` |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Foreign Keys:** `tenant_id` -> [[#`tenants`|tenants]], `file_record_id` -> [[#`file_records`|file_records]]

**Rules:** raw `owner_type` and `asset_purpose` values are backend classifications, not normal UI labels. Frontend clients must use purpose-specific APIs such as profile-photo, tenant-logo, project-cover, or support-ticket attachment endpoints; they must not submit arbitrary owner type/id pairs.

---

## `tenants`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `name` | `varchar(200)` | Company name |
| `slug` | `varchar(100)` | URL-safe identifier, UNIQUE |
| `primary_contact_email` | `varchar(255)` | Primary customer contact captured during Developer Platform tenant profile creation |
| `country_code` | `varchar(3)` | Tenant profile country code selected during provisioning |
| `industry_profile` | `varchar(30)` | `office_it`, `manufacturing`, `retail`, `healthcare`, `custom` - sets monitoring defaults during provisioning/demo approval |
| `registration_profile_name` | `varchar(200)` | Registration/profile display name captured on the tenant profile, not a legal entity name |
| `registration_number` | `varchar(50)` | Nullable registration/profile number captured on the tenant profile |
| `company_size_range` | `varchar(30)` | Employee-count range captured during Developer Platform provisioning, e.g. `1-50`, `51-200`, `201-500` |
| `timezone` | `varchar(50)` | Tenant default IANA timezone selected during profile setup |
| `currency_code` | `varchar(3)` | Tenant default ISO 4217 currency selected during profile setup |
| `status` | `varchar(20)` | `provisioning`, `trial`, `trial_expired`, `pending_payment`, `active`, `suspended`, `cancelled` |
| `subscription_plan_id` | `uuid` | FK -> subscription_plans |
| `settings_json` | `jsonb` | Tenant-level settings |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `subscription_plan_id` -> [[database/schemas/shared-platform#`subscription_plans`|subscription_plans]]

**Status semantics:**

- `provisioning` - Developer Platform draft tenant. Visible to `/admin/v1/*` operators, excluded from tenant-facing `/api/v1/*`, login, analytics, and normal customer workflows until activation.
- `trial` - Activated tenant in a time-limited trial/commercial evaluation state.
- `active` - Activated production tenant with tenant-facing access enabled.
- `suspended` - Temporarily disabled tenant. Data is preserved; tenant-facing login and workflows are blocked.
- `cancelled` - Commercially cancelled/offboarded tenant. Data retention, export, and purge follow the offboarding policy.

`country_code`, `registration_profile_name`, `registration_number`, `company_size_range`, `timezone`, and `currency_code` are tenant profile metadata, not legal entity data. Detailed provisioning progress is stored in `tenant_provisioning_states` and `tenant_provisioning_validation_results`; do not add wizard-step progress columns to `tenants`.

Tenant profile creation seeds one default legal entity for single-company setup. Multi-company customers can add additional legal entities in customer-app after activation.

---

## `users`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `email` | `varchar(255)` | UNIQUE per tenant |
| `password_hash` | `varchar(255)` | BCrypt hash, work factor 12 |
| `first_name` | `varchar(100)` |  |
| `last_name` | `varchar(100)` |  |
| `is_active` | `boolean` |  |
| `email_verified` | `boolean` |  |
| `last_login_at` | `timestamptz` | Nullable |
| `must_change_password` | `boolean` | Security reset flag; not used as an invite method |
| `password_setup_required` | `boolean` | True until invited user completes password setup; SSO can still be used when enabled |
| `password_setup_expires_at` | `timestamptz` | Nullable - expiry for account setup link; admin can resend invite |
| `password_reset_token_hash` | `varchar(128)` | Nullable - SHA-256 hex hash of the forgot-password reset token |
| `password_reset_token_expires_at` | `timestamptz` | Nullable - 1-hour expiry for password reset tokens |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` | Nullable |
| `is_deleted` | `boolean` | Soft delete |
| `created_by_id` | `uuid` | FK -> users (who created this record) |

**Foreign Keys:** `tenant_id` -> [[#`tenants`|tenants]]

---

## Related

- [[modules/infrastructure/overview|Infrastructure Module]]
- [[modules/auth/overview|Auth Module]] - authentication and token services use this table
- [[backend/api-conventions|API Conventions]] - first-party API auth and endpoint conventions
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]


