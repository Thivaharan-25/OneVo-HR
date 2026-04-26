# Documents — Schema

**Module:** [[modules/documents/overview|Documents]]
**Phase:** Phase 2
**Tables:** 6

---

## `document_access_logs`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `document_version_id` | `uuid` | FK → document_versions |
| `employee_id` | `uuid` | FK → employees |
| `action` | `varchar(20)` | `view`, `download`, `print` |
| `accessed_at` | `timestamptz` |  |
| `ip_address` | `varchar(45)` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `document_version_id` → [[#`document_versions`|document_versions]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]]

---

## `document_acknowledgements`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `document_version_id` | `uuid` | FK → document_versions |
| `employee_id` | `uuid` | FK → employees |
| `acknowledged_by_id` | `uuid` | FK → users (may differ from employee if acknowledged on behalf) |
| `method` | `varchar(20)` | `click`, `e_signature` |
| `acknowledged_at` | `timestamptz` |  |
| `ip_address` | `varchar(45)` | IPv4/IPv6 for audit |

**Foreign Keys:** `document_version_id` → [[#`document_versions`|document_versions]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]], `acknowledged_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## `document_categories`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `parent_category_id` | `uuid` | FK → document_categories (nullable — null for root) |
| `name` | `varchar(100)` |  |
| `applies_to` | `varchar(30)` | `company`, `department`, `employee` |
| `is_active` | `boolean` |  |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `parent_category_id` → [[#`document_categories`|document_categories]]

---

## `document_templates`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(100)` |  |
| `category_id` | `uuid` | FK → document_categories (nullable) |
| `template_content` | `text` | HTML/Markdown template body |
| `variables_json` | `jsonb` | Available merge variables (e.g., `{{employee_name}}`) |
| `is_active` | `boolean` |  |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `category_id` → [[#`document_categories`|document_categories]], `created_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## `document_versions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `document_id` | `uuid` | FK → documents |
| `version_number` | `integer` | Auto-incremented per document |
| `blob_storage_url` | `varchar(500)` | Signed URL or blob path |
| `file_name` | `varchar(255)` | Original file name |
| `effective_date` | `date` | When this version takes effect |
| `expiry_date` | `date` | Nullable |
| `is_current` | `boolean` | Only one current version per document |
| `uploaded_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `document_id` → [[#`documents`|documents]], `uploaded_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## `documents`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `legal_entity_id` | `uuid` | FK → legal_entities (nullable) |
| `category_id` | `uuid` | FK → document_categories |
| `employee_id` | `uuid` | FK → employees (nullable — null for company-wide docs) |
| `title` | `varchar(255)` |  |
| `requires_acknowledgement` | `boolean` | Whether employees must acknowledge receipt |
| `is_active` | `boolean` |  |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `legal_entity_id` → [[database/schemas/org-structure#`legal_entities`|legal_entities]], `category_id` → [[#`document_categories`|document_categories]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]], `created_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## Messaging Tables (MassTransit Outbox + Idempotency)

> These tables are managed by MassTransit and must not be written to directly. They are part of each module's DbContext.

### `documents_outbox_events`

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

### `processed_integration_events`

Idempotency table — prevents double-processing if RabbitMQ redelivers a message.

| Column | Type | Notes |
|:-------|:-----|:------|
| `event_id` | `uuid` | PK — same as `IntegrationEvent.EventId` |
| `event_type` | `varchar(200)` | |
| `processed_at` | `timestamptz` | |

---

## Related

- [[modules/documents/overview|Documents Module]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]