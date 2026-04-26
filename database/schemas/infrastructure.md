# Infrastructure — Schema

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

## `bridge_clients`

OAuth 2.0 clients for service-to-service bridge API access. Managed by Auth module.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK — used as `client_id` in OAuth flow |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(100)` | e.g., "WorkManage Pro" |
| `client_secret_hash` | `varchar(255)` | Argon2id hash of the secret (shown once at registration) |
| `allowed_bridges` | `text[]` | Bridge names allowed: e.g., `["people-sync", "availability"]` |
| `is_active` | `boolean` | False = revoked |
| `created_by` | `uuid` | FK → users |
| `created_at` | `timestamptz` | |
| `last_used_at` | `timestamptz` | Updated on each token issuance |

UNIQUE: `(tenant_id, name)`

**Foreign Keys:** `tenant_id` → [[#`tenants`|tenants]], `created_by` → [[#`users`|users]]

---

## Messaging Tables (MassTransit Outbox)

> These tables are managed by MassTransit and must not be written to directly. They are part of each module's DbContext.

### `infrastructure_outbox_events`

Transactional outbox — written in the same DB transaction as the business write. A background processor reads and forwards to RabbitMQ.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `event_type` | `varchar(200)` | Fully-qualified event class name |
| `payload` | `jsonb` | Serialized IntegrationEvent |
| `created_at` | `timestamptz` | |
| `processed_at` | `timestamptz` | NULL = not yet delivered to RabbitMQ |
| `retry_count` | `integer` | Default 0; max 5 |
| `last_error` | `text` | Last failure message if any |

Index: `WHERE processed_at IS NULL` on `created_at` — the outbox processor queries this.

---

## Related

- [[modules/infrastructure/overview|Infrastructure Module]]
- [[modules/auth/overview|Auth Module]] — `IBridgeAuthService` uses this table
- [[backend/bridge-api-contracts|Bridge API Contracts]] — auth flow and endpoint contracts
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]