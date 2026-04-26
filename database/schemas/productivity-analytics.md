# Productivity Analytics — Schema

**Module:** [[modules/productivity-analytics/overview|Productivity Analytics]]
**Phase:** Phase 1
**Tables:** 5

---

## `daily_employee_report`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `date` | `date` |  |
| `total_hours` | `decimal(5,2)` | From presence sessions |
| `active_hours` | `decimal(5,2)` | From activity summaries |
| `idle_hours` | `decimal(5,2)` |  |
| `meeting_hours` | `decimal(5,2)` |  |
| `active_percentage` | `decimal(5,2)` |  |
| `top_apps_json` | `jsonb` | Top 5 apps with time |
| `intensity_score` | `decimal(5,2)` | Average intensity for the day |
| `device_split_json` | `jsonb` | `{"laptop": 85, "mobile_estimate": 15}` |
| `exceptions_count` | `int` | Alerts triggered this day |
| `anomaly_flags_json` | `jsonb` | Flagged anomalies |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]]

---

## `monthly_employee_report`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `year` | `int` |  |
| `month` | `int` | 1–12 |
| `total_hours` | `decimal(7,2)` |  |
| `active_hours` | `decimal(7,2)` |  |
| `idle_hours` | `decimal(7,2)` |  |
| `meeting_hours` | `decimal(7,2)` |  |
| `active_percentage` | `decimal(5,2)` |  |
| `intensity_avg` | `decimal(5,2)` |  |
| `exceptions_count` | `int` |  |
| `performance_pattern_json` | `jsonb` | Weekday patterns, peak hours |
| `comparative_rank_in_department` | `int` | Rank by active% within department |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]]

---

## `weekly_employee_report`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `week_start` | `date` | Monday of the week |
| `total_hours` | `decimal(6,2)` |  |
| `active_hours` | `decimal(6,2)` |  |
| `idle_hours` | `decimal(6,2)` |  |
| `meeting_hours` | `decimal(6,2)` |  |
| `active_percentage` | `decimal(5,2)` |  |
| `intensity_avg` | `decimal(5,2)` |  |
| `exceptions_count` | `int` |  |
| `trend_vs_previous_week_json` | `jsonb` | `{"active_pct_change": +5.2, "hours_change": -0.5}` |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]]

---

## `workforce_snapshot`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `date` | `date` |  |
| `total_employees` | `int` | Active employees count |
| `active_count` | `int` | Employees with activity this day |
| `avg_active_percentage` | `decimal(5,2)` | Tenant-wide average |
| `avg_meeting_percentage` | `decimal(5,2)` |  |
| `total_exceptions` | `int` | Total alerts generated |
| `top_exception_types_json` | `jsonb` | Most common exception types |
| `department_breakdown_json` | `jsonb` | Per-department active% |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `wms_productivity_snapshots`

WMS-submitted task productivity metrics per employee per period. Populated via the Productivity Metrics bridge (`POST /api/v1/bridges/productivity-metrics/snapshots`). This is the Phase 1 landing table for WMS performance data — allows the bridge to receive data immediately without waiting for the Phase 2 Performance module. Phase 2 Performance module reads from this table alongside agent-based scores.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `period_type` | `varchar(10)` | `daily`, `weekly`, `monthly` |
| `period_start` | `date` | |
| `period_end` | `date` | |
| `tasks_completed` | `int` | |
| `tasks_on_time` | `int` | |
| `on_time_delivery_rate` | `decimal(5,2)` | 0–100 percentage |
| `productivity_score` | `decimal(5,2)` | WMS-calculated composite score (0–100) |
| `active_projects_count` | `int` | |
| `velocity_story_points` | `int` | Nullable — only for agile teams |
| `submitted_at` | `timestamptz` | When WMS submitted this snapshot |
| `created_at` | `timestamptz` | |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]]

**Index:** `(tenant_id, employee_id, period_type, period_start)` UNIQUE

**Visibility:** Admin and Reporting Manager only. Not surfaced to the employee directly.

---

## Messaging Tables (MassTransit Outbox + Idempotency)

> These tables are managed by MassTransit and must not be written to directly. They are part of each module's DbContext.

### `productivity_analytics_outbox_events`

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

- [[modules/productivity-analytics/overview|Productivity Analytics Module]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]