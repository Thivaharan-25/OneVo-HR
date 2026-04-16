# Discrepancy Engine — Schema

**Module:** [[modules/discrepancy-engine/overview|Discrepancy Engine]]
**Phase:** Phase 1
**Tables:** 2

> These tables were previously grouped under the Activity Monitoring schema file. Split out because they are owned and written to by `ONEVO.Modules.DiscrepancyEngine`, not Activity Monitoring.

---

## `discrepancy_events`

Daily discrepancy detection results — comparing HR active time (from agent) vs WMS-reported task time vs calendar-explained time. Written by `DiscrepancyEngineJob` (daily 10:30 PM). Read by managers, HR Admins, and Productivity Analytics.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `date` | `date` | |
| `hr_active_minutes` | `int` | Ground truth from `activity_daily_summary` |
| `wms_logged_minutes` | `int` | What employee logged in WMS task time |
| `calendar_minutes` | `int` | Explained time from `calendar_events` (meetings, OOO) |
| `unaccounted_minutes` | `int` | Computed: `hr_active - wms_logged - calendar`. Negative = under-reporter |
| `severity` | `varchar(20)` | `none`, `low`, `high`, `critical` — based on tenant threshold config |
| `threshold_minutes` | `int` | Tenant-configured acceptable gap (default 60 min) |
| `notified_manager` | `boolean` | Whether manager was alerted |
| `notified_at` | `timestamptz` | Nullable |
| `created_at` | `timestamptz` | |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]]

**Index:** `(tenant_id, employee_id, date)`, `(tenant_id, severity, date)`

**Visibility:** Discrepancy data is visible ONLY to the reporting manager and HR Admin. Employee never sees their own discrepancy record — only their personal activity timeline. Enforced at query level (`RequirePermission("exceptions:manage")`), not just UI level.

**Severity thresholds (default, tenant-configurable):**
- `none` — unaccounted gap < 30 min
- `low` — 30–60 min gap (automated reminder to employee to log time)
- `high` — 60–180 min gap (manager notified privately)
- `critical` — 180+ min gap (escalated to HR Admin)

---

## `wms_daily_time_logs`

WMS-submitted task time per employee per day. Populated by the Work Activity bridge (`POST /api/v1/bridges/work-activity/time-logs`). Consumed by `DiscrepancyEngineJob` as the `wms_logged_minutes` input stream. Upserted — re-submission for same employee + date overwrites.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `date` | `date` | |
| `total_logged_minutes` | `int` | Aggregated from all task log entries for this day |
| `active_task_at` | `timestamptz` | Most recent active task timestamp (nullable — real-time context) |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]]

**Index:** `(tenant_id, employee_id, date)` UNIQUE

**Note:** If no WMS integration exists, this table stays empty. Discrepancy Engine skips it gracefully (`wms_logged_minutes = 0`, only calendar cross-reference used).

---

## Related

- [[modules/discrepancy-engine/overview|Discrepancy Engine Module]]
- [[database/schemas/activity-monitoring|Activity Monitoring Schema]] — source of `activity_daily_summary` (input to discrepancy calculation)
- [[database/schemas/core-hr|Core HR Schema]] — `employees` table
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
