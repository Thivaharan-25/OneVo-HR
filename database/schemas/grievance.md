# Grievance — Schema

**Module:** [[modules/grievance/overview|Grievance]]
**Phase:** Phase 2
**Tables:** 2

---

## `disciplinary_actions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `employee_id` | `uuid` | FK → employees |
| `grievance_id` | `uuid` | FK → grievance_cases (nullable) |
| `action_type` | `varchar(30)` | `verbal_warning`, `written_warning`, `suspension`, `termination` |
| `description` | `text` |  |
| `effective_date` | `date` |  |
| `issued_by_id` | `uuid` | FK → users |
| `acknowledged_at` | `timestamptz` | Employee acknowledgement |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `employee_id` → [[database/schemas/core-hr#`employees`|employees]], `grievance_id` → [[#`grievance_cases`|grievance_cases]], `issued_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## `grievance_cases`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `filed_by_id` | `uuid` | FK → employees (nullable if anonymous) |
| `against_id` | `uuid` | FK → employees (nullable) |
| `category` | `varchar(30)` | `harassment`, `discrimination`, `safety`, `policy_violation`, `other` |
| `description` | `text` |  |
| `severity` | `varchar(20)` | `low`, `medium`, `high`, `critical` |
| `status` | `varchar(20)` | `filed`, `investigating`, `resolved`, `dismissed`, `escalated` |
| `resolution` | `text` |  |
| `resolved_by_id` | `uuid` | FK → users |
| `resolved_at` | `timestamptz` |  |
| `is_anonymous` | `boolean` |  |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `filed_by_id` → [[database/schemas/core-hr#`employees`|employees]], `against_id` → [[database/schemas/core-hr#`employees`|employees]], `resolved_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## Messaging Tables (MassTransit Outbox)

> These tables are managed by MassTransit and must not be written to directly. They are part of each module's DbContext.

### `grievance_outbox_events`

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

- [[modules/grievance/overview|Grievance Module]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]