# Productivity Analytics - Schema

**Module:** [[modules/productivity-analytics/overview|Productivity Analytics]]
**Phase:** Phase 1
**Tables:** 5

---

## `daily_employee_report`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `date` | `date` |  |
| `total_hours` | `decimal(5,2)` | From presence sessions |
| `active_hours` | `decimal(5,2)` | From activity summaries |
| `idle_hours` | `decimal(5,2)` |  |
| `meeting_hours` | `decimal(5,2)` |  |
| `active_percentage` | `decimal(5,2)` | Activity rate, not final productivity |
| `productive_app_hours` | `decimal(5,2)` | Work-classified app/domain time |
| `focus_hours` | `decimal(5,2)` | Deep-focus time |
| `activity_score` | `decimal(5,2)` | Monitoring-derived score, 0-100 |
| `work_output_score` | `decimal(5,2)` | Nullable WorkSync output score |
| `productivity_score` | `decimal(5,2)` | Final score for reporting/reviews |
| `productivity_score_basis` | `varchar(30)` | `composite`, `activity_only`, `worksync_only`, `insufficient_data` |
| `data_coverage_percentage` | `decimal(5,2)` | Evidence completeness/confidence |
| `top_apps_json` | `jsonb` | Top 5 apps with time |
| `intensity_score` | `decimal(5,2)` | Average intensity for the day |
| `device_split_json` | `jsonb` | `{"laptop": 85, "mobile_estimate": 15}` |
| `exceptions_count` | `int` | Alerts triggered this day |
| `anomaly_flags_json` | `jsonb` | Flagged anomalies |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` -> [[database/schemas/core-hr#`employees`|employees]]

---

## `monthly_employee_report`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `year` | `int` |  |
| `month` | `int` | 1-12 |
| `total_hours` | `decimal(7,2)` |  |
| `active_hours` | `decimal(7,2)` |  |
| `idle_hours` | `decimal(7,2)` |  |
| `meeting_hours` | `decimal(7,2)` |  |
| `active_percentage` | `decimal(5,2)` | Activity rate |
| `productive_app_hours` | `decimal(7,2)` |  |
| `focus_hours` | `decimal(7,2)` |  |
| `activity_score_avg` | `decimal(5,2)` |  |
| `work_output_score_avg` | `decimal(5,2)` | Nullable |
| `productivity_score` | `decimal(5,2)` |  |
| `productivity_score_basis` | `varchar(30)` | `composite`, `activity_only`, `worksync_only`, `insufficient_data` |
| `data_coverage_percentage` | `decimal(5,2)` |  |
| `intensity_avg` | `decimal(5,2)` |  |
| `exceptions_count` | `int` |  |
| `performance_pattern_json` | `jsonb` | Weekday patterns, peak hours |
| `comparative_rank_in_department` | `int` | Rank by active% within department |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` -> [[database/schemas/core-hr#`employees`|employees]]

---

## `weekly_employee_report`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `week_start` | `date` | Monday of the week |
| `total_hours` | `decimal(6,2)` |  |
| `active_hours` | `decimal(6,2)` |  |
| `idle_hours` | `decimal(6,2)` |  |
| `meeting_hours` | `decimal(6,2)` |  |
| `active_percentage` | `decimal(5,2)` | Activity rate |
| `productive_app_hours` | `decimal(6,2)` |  |
| `focus_hours` | `decimal(6,2)` |  |
| `activity_score_avg` | `decimal(5,2)` |  |
| `work_output_score_avg` | `decimal(5,2)` | Nullable |
| `productivity_score` | `decimal(5,2)` |  |
| `productivity_score_basis` | `varchar(30)` | `composite`, `activity_only`, `worksync_only`, `insufficient_data` |
| `data_coverage_percentage` | `decimal(5,2)` |  |
| `intensity_avg` | `decimal(5,2)` |  |
| `exceptions_count` | `int` |  |
| `trend_vs_previous_week_json` | `jsonb` | `{"active_pct_change": +5.2, "hours_change": -0.5}` |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` -> [[database/schemas/core-hr#`employees`|employees]]

---

## `monitoring_snapshot`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `date` | `date` |  |
| `total_employees` | `int` | Active employees count |
| `active_count` | `int` | Employees with activity this day |
| `avg_active_percentage` | `decimal(5,2)` | Tenant-wide activity-rate average |
| `avg_activity_score` | `decimal(5,2)` |  |
| `avg_work_output_score` | `decimal(5,2)` | Nullable |
| `avg_productivity_score` | `decimal(5,2)` |  |
| `avg_data_coverage_percentage` | `decimal(5,2)` |  |
| `avg_meeting_percentage` | `decimal(5,2)` |  |
| `total_exceptions` | `int` | Total alerts generated |
| `top_exception_types_json` | `jsonb` | Most common exception types |
| `department_breakdown_json` | `jsonb` | Per-department active% |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `wms_productivity_snapshots`

Work Management-derived task productivity metrics per employee per period. Populated internally from Work Management task, sprint, time, and delivery records when Work Management is enabled. Phase 2 Performance can read from this table alongside agent-based scores.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `period_type` | `varchar(10)` | `daily`, `weekly`, `monthly` |
| `period_start` | `date` | |
| `period_end` | `date` | |
| `tasks_completed` | `int` | |
| `tasks_on_time` | `int` | |
| `on_time_delivery_rate` | `decimal(5,2)` | 0-100 percentage |
| `work_output_score` | `decimal(5,2)` | Work Management-calculated output score (0-100) |
| `productivity_score` | `decimal(5,2)` | Deprecated alias for `work_output_score` during migration; do not use for new code |
| `active_projects_count` | `int` | |
| `submitted_at` | `timestamptz` | When Work Management submitted this snapshot |
| `created_at` | `timestamptz` | |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` -> [[database/schemas/core-hr#`employees`|employees]]

**Index:** `(tenant_id, employee_id, period_type, period_start)` UNIQUE

**Visibility:** Authorized analytics users, recipients resolved by Monitoring Policy, and configured reviewers only. Not surfaced to the employee directly.

---

## Related

- [[modules/productivity-analytics/overview|Productivity Analytics Module]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]
