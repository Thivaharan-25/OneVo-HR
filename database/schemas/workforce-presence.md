# Workforce Presence — Schema

**Module:** [[modules/workforce-presence/overview|Workforce Presence]]
**Phase:** Phase 1
**Tables:** 12

---

## `break_records`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `break_start` | `timestamptz` |  |
| `break_end` | `timestamptz` | Null if ongoing |
| `break_type` | `varchar(30)` | `lunch`, `prayer`, `smoke`, `personal`, `other` |
| `auto_detected` | `boolean` | True if detected by agent idle threshold |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]]

---

## `device_sessions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `device_id` | `uuid` | FK → registered_agents |
| `session_start` | `timestamptz` | When active period began |
| `session_end` | `timestamptz` | When active period ended (null if ongoing) |
| `active_minutes` | `int` | Minutes with input activity |
| `idle_minutes` | `int` | Minutes without input |
| `active_percentage` | `decimal(5,2)` | `active / (active + idle) * 100` |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]], `device_id` → [[database/schemas/agent-gateway#`registered_agents`|registered_agents]]

---

## `presence_sessions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `date` | `date` | The work day |
| `first_seen_at` | `timestamptz` | First sign of presence (any source) |
| `last_seen_at` | `timestamptz` | Last sign of presence |
| `total_present_minutes` | `int` | Computed from all sources |
| `total_break_minutes` | `int` | Sum of break records |
| `source` | `varchar(20)` | `biometric`, `agent`, `manual`, `mixed` |
| `status` | `varchar(20)` | `present`, `absent`, `partial`, `on_leave` |
| `created_at` | `timestamptz` | Audit |
| `updated_at` | `timestamptz` | Audit |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]]

---

## `attendance_records`

Daily attendance summary per employee — one row per employee per work day.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `date` | `date` | The work day |
| `scheduled_start` | `time` | From shift_assignments for that day |
| `scheduled_end` | `time` | From shift_assignments for that day |
| `actual_start` | `timestamptz` | First check-in (biometric or agent) |
| `actual_end` | `timestamptz` | Last check-out |
| `worked_minutes` | `int` | Total clocked time minus breaks |
| `status` | `varchar(20)` | `present`, `absent`, `late`, `half_day`, `on_leave` |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]]

---

## `employee_schedules`

Which work schedule an employee follows, and for what date range.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `work_schedule_id` | `uuid` | FK → work_schedules |
| `effective_from` | `date` |  |
| `effective_to` | `date` | Nullable — null means currently active |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]], `work_schedule_id` → [[#`work_schedules`|work_schedules]]

---

## `overtime_records`

Logged overtime per employee per day.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `date` | `date` |  |
| `overtime_minutes` | `int` | Minutes worked beyond scheduled end |
| `reason` | `varchar(255)` | Nullable |
| `approved_by_id` | `uuid` | FK → employees (nullable) |
| `status` | `varchar(20)` | `pending`, `approved`, `rejected` |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]], `approved_by_id` → [[database/schemas/core-hr#`employees`|employees]]

---

## `public_holidays`

Country-level or tenant-level non-working days.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants (nullable — null means country-default) |
| `country_id` | `uuid` | FK → countries |
| `date` | `date` |  |
| `name` | `varchar(100)` | e.g., "National Day" |
| `is_mandatory` | `boolean` | False allows tenant-level override |

**Foreign Keys:** `country_id` → [[database/schemas/infrastructure#`countries`|countries]]

---

## `roster_entries`

An employee's placement within a roster period.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `roster_period_id` | `uuid` | FK → roster_periods |
| `employee_id` | `uuid` | FK → employees |
| `shift_id` | `uuid` | FK → shifts |
| `date` | `date` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `roster_period_id` → [[#`roster_periods`|roster_periods]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]], `shift_id` → [[#`shifts`|shifts]]

---

## `roster_periods`

A planning window for shift rosters (e.g., a single week or fortnight).

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(100)` | e.g., "Week 15 — Apr 7–13" |
| `start_date` | `date` |  |
| `end_date` | `date` |  |
| `status` | `varchar(20)` | `draft`, `published`, `locked` |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `created_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## `shift_assignments`

Maps an employee to a specific shift for a specific date.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `shift_id` | `uuid` | FK → shifts |
| `date` | `date` |  |
| `is_override` | `boolean` | True if manually overriding the employee's default schedule |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]], `shift_id` → [[#`shifts`|shifts]]

---

## `shifts`

Named shift definitions — the reusable building blocks of schedules.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(100)` | e.g., "Morning Shift", "Night Shift" |
| `start_time` | `time` | e.g., `09:00` |
| `end_time` | `time` | e.g., `18:00` |
| `break_minutes` | `int` | Expected total break duration |
| `is_overnight` | `boolean` | True if end_time < start_time |
| `is_active` | `boolean` |  |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `work_schedules`

Named weekly schedule templates — defines which shift applies on which day.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(100)` | e.g., "Standard 5-Day", "4-Day Compressed" |
| `days_json` | `jsonb` | Map of day → shift_id: `{"mon": "<uuid>", "tue": "<uuid>", ..., "sun": null}` |
| `is_active` | `boolean` |  |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]]

---

## Messaging Tables (MassTransit Outbox + Idempotency)

> These tables are managed by MassTransit and must not be written to directly. They are part of each module's DbContext.

### `workforce_presence_outbox_events`

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

- [[modules/workforce-presence/overview|Workforce Presence Module]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]