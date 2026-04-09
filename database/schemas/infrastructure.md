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
| `status` | `varchar(20)` | `trial`, `active`, `suspended`, `cancelled` |
| `subscription_plan_id` | `uuid` | FK → subscription_plans |
| `settings_json` | `jsonb` | Tenant-level settings |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `subscription_plan_id` → [[database/schemas/shared-platform#`subscription_plans`|subscription_plans]]

---

## `users`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `email` | `varchar(255)` | UNIQUE per tenant |
| `password_hash` | `varchar(255)` | bcrypt |
| `is_active` | `boolean` |  |
| `email_verified` | `boolean` |  |
| `last_login_at` | `timestamptz` |  |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[#`tenants`|tenants]]

---

## Related

- [[modules/infrastructure/overview|Infrastructure Module]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]