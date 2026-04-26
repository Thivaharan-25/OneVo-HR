# Exception Engine — Schema

**Module:** [[modules/exception-engine/overview|Exception Engine]]
**Phase:** Phase 1
**Tables:** 5

---

## `alert_acknowledgements`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `alert_id` | `uuid` | FK → exception_alerts |
| `acknowledged_by_id` | `uuid` | FK → users |
| `action` | `varchar(20)` | `acknowledged`, `dismissed`, `escalated`, `noted` |
| `comment` | `text` | Optional note |
| `acted_at` | `timestamptz` |  |

**Foreign Keys:** `alert_id` → [[#`exception_alerts`|exception_alerts]], `acknowledged_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## `escalation_chains`

> **Scope:** Alert routing for system-detected anomalies (GPS mismatch, excessive idle, unusual activity). Triggered by `exception_alerts`. See [[database/schemas/shared-platform#`escalation_rules`|escalation_rules]] for workflow SLA timeouts (leave pending >N hours etc.) — those are a separate system.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `severity` | `varchar(20)` | Which severity triggers this chain |
| `step_order` | `int` | 1, 2, 3… |
| `notify_role` | `varchar(30)` | `reporting_manager`, `department_head`, `hr`, `ceo`, `custom` |
| `notify_user_id` | `uuid` | Nullable — for `custom` role |
| `delay_minutes` | `int` | Wait N minutes before escalating to next step |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `exception_alerts`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `rule_id` | `uuid` | FK → exception_rules |
| `triggered_at` | `timestamptz` | When the rule fired |
| `severity` | `varchar(20)` | Copied from rule at trigger time |
| `summary` | `varchar(500)` | Human-readable description |
| `data_snapshot_json` | `jsonb` | Evidence data at trigger time |
| `status` | `varchar(20)` | `new`, `acknowledged`, `dismissed`, `escalated` |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]], `rule_id` → [[#`exception_rules`|exception_rules]]

---

## `exception_rules`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `rule_name` | `varchar(100)` | Human-readable name |
| `rule_type` | `varchar(30)` | `low_activity`, `excess_idle`, `unusual_pattern`, `excess_meeting`, `no_presence`, `break_exceeded`, `verification_failed`, `non_allowed_app`, `presence_without_activity`, `heartbeat_gap` |
| `threshold_json` | `jsonb` | Rule-specific thresholds (see below) |
| `severity` | `varchar(20)` | `info`, `warning`, `critical` |
| `is_active` | `boolean` |  |
| `applies_to` | `varchar(20)` | `all`, `department`, `team`, `employee` |
| `applies_to_id` | `uuid` | Nullable — department/team/employee ID |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `created_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## `exception_schedules`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants, UNIQUE |
| `check_interval_minutes` | `int` | Default 5 |
| `active_from_time` | `time` | e.g., 08:00 |
| `active_to_time` | `time` | e.g., 18:00 |
| `active_days_json` | `jsonb` | e.g., `[1,2,3,4,5]` (Mon–Fri) |
| `timezone` | `varchar(50)` | e.g., "Asia/Colombo" |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]]

---

## Messaging Tables (MassTransit Outbox + Idempotency)

> These tables are managed by MassTransit and must not be written to directly. They are part of each module's DbContext.

### `exception_engine_outbox_events`

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

- [[modules/exception-engine/overview|Exception Engine Module]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]