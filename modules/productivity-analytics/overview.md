# Module: Productivity Analytics

**Feature Folder:** `Application/Features/ProductivityAnalytics`
**Phase:** 1 - Build
**Pillar:** 2 - Monitoring
**Owner:** Dev 1 (Week 4)
**Tables:** 5
**Task File:** [[current-focus/DEV1-productivity-analytics|DEV1: Productivity Analytics]]

---

## Purpose

Aggregates data from [[modules/activity-monitoring/overview|Activity Monitoring]], [[modules/time-attendance/overview|Time & Attendance]], [[modules/core-hr/overview|Core Hr]], and optional WorkSync output signals into daily/weekly/monthly reports and monitoring-wide snapshots. Serves both the dashboard API and CSV/Excel export. This is the **reporting layer** for Pillar 2.

Productivity Analytics separates monitoring evidence from output evidence:

| Metric | Meaning | Primary Sources |
|:-------|:--------|:----------------|
| `activity_score` | How consistently the employee was present and active during valid work windows | Presence sessions, active/idle minutes, meeting minutes, data coverage |
| `work_output_score` | How much assigned work moved forward with quality and timeliness | WorkSync tasks, approvals, sprint reports, time logs, OKR progress |
| `productivity_score` | Composite score when output evidence is available; otherwise an activity-derived fallback that must be labelled in the UI | `activity_score`, `work_output_score`, exception adjustments |
| `data_coverage_percentage` | How complete the evidence is for the period | Presence sessions, agent heartbeat/device coverage, WorkSync availability |

`active_percentage` is an activity rate, not a productivity score. UI copy must not call it "productivity" unless it is part of the composite score.

**Three dashboard views:**
2. **Executive Dashboard** - high-level monitoring summary, exception-only escalation, no individual drill-down unless flagged
3. **Employee Self-Service** - own data only (hours, activity rate, work-classified app time, score basis, trends). Cannot see other employees.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[modules/activity-monitoring/overview\|Activity Monitoring]] | `IActivityMonitoringService` | Daily summaries for aggregation |
| **Depends on** | [[modules/time-attendance/overview\|Time & Attendance]] | `ITimeAttendanceService` | Attendance/hours data |
| **Depends on** | [[modules/core-hr/overview\|Core Hr]] | `IEmployeeService` | Employee/department context |
| **Depends on** | [[modules/exception-engine/overview\|Exception Engine]] | `IExceptionEngineService` | Exception counts per day |
| **Depends on** | [[modules/work-management/analytics/overview|Work Analytics]] | `IWorkSyncAnalyticsService` | Optional task completion, delivery, and productivity signals from internal WorkSync modules |
| **Consumed by** | [[database/performance\|Performance]] | `IProductivityAnalyticsService` | Productivity scores for reviews |
| **Consumed by** | [[modules/reporting-engine/overview\|Reporting Engine]] | - (via query) | Scheduled report generation |

---

## Public Interface

```csharp
// ONEVO.Application.Features.ProductivityAnalytics/Public/IProductivityAnalyticsService.cs
public interface IProductivityAnalyticsService
{
    Task<Result<DailyEmployeeReportDto>> GetDailyReportAsync(Guid employeeId, DateOnly date, CancellationToken ct);
    Task<Result<WeeklyEmployeeReportDto>> GetWeeklyReportAsync(Guid employeeId, DateOnly weekStart, CancellationToken ct);
    Task<Result<MonthlyEmployeeReportDto>> GetMonthlyReportAsync(Guid employeeId, int year, int month, CancellationToken ct);
    Task<Result<MonitoringSnapshotDto>> GetMonitoringSnapshotAsync(DateOnly date, CancellationToken ct);
    Task<Result<decimal>> GetProductivityScoreAsync(Guid employeeId, DateOnly from, DateOnly to, CancellationToken ct);
}
```

---

## Code Location (Clean Architecture)

Domain entities:
  ONEVO.Domain/Features/ProductivityAnalytics/Entities/
  ONEVO.Domain/Features/ProductivityAnalytics/Events/

Application (CQRS):
  ONEVO.Application/Features/ProductivityAnalytics/Commands/
  ONEVO.Application/Features/ProductivityAnalytics/Queries/
  ONEVO.Application/Features/ProductivityAnalytics/DTOs/Requests/
  ONEVO.Application/Features/ProductivityAnalytics/DTOs/Responses/
  ONEVO.Application/Features/ProductivityAnalytics/Validators/
  ONEVO.Application/Features/ProductivityAnalytics/EventHandlers/

Infrastructure:
  ONEVO.Infrastructure/Persistence/Configurations/ProductivityAnalytics/

API endpoints:
  ONEVO.Api/Controllers/ProductivityAnalytics/ProductivityAnalyticsController.cs

---

## Database Tables (5)

### `daily_employee_report`

One row per employee per day.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `date` | `date` | |
| `total_hours` | `decimal(5,2)` | From presence sessions |
| `active_hours` | `decimal(5,2)` | From activity summaries |
| `idle_hours` | `decimal(5,2)` | |
| `meeting_hours` | `decimal(5,2)` | |
| `active_percentage` | `decimal(5,2)` | Activity rate: `active / (active + idle) * 100` |
| `productive_app_hours` | `decimal(5,2)` | Work-classified app/domain time from activity summary |
| `focus_hours` | `decimal(5,2)` | Deep-focus time from activity summary |
| `activity_score` | `decimal(5,2)` | Monitoring-derived score, 0-100 |
| `work_output_score` | `decimal(5,2)` | Nullable; populated when WorkSync output data exists |
| `productivity_score` | `decimal(5,2)` | Final score shown for reviews/reporting |
| `productivity_score_basis` | `varchar(30)` | `composite`, `activity_only`, `worksync_only`, `insufficient_data` |
| `data_coverage_percentage` | `decimal(5,2)` | Confidence/completeness of evidence |
| `top_apps_json` | `jsonb` | Top 5 apps with time |
| `intensity_score` | `decimal(5,2)` | Average intensity for the day |
| `device_split_json` | `jsonb` | `{"laptop": 85, "mobile_estimate": 15}` |
| `exceptions_count` | `int` | Alerts triggered this day |
| `anomaly_flags_json` | `jsonb` | Flagged anomalies |
| `created_at` | `timestamptz` | |

**Indexes:** `(tenant_id, employee_id, date)` UNIQUE, `(tenant_id, date)`

### `weekly_employee_report`

Weekly aggregation.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `week_start` | `date` | Monday of the week |
| `total_hours` | `decimal(6,2)` | |
| `active_hours` | `decimal(6,2)` | |
| `idle_hours` | `decimal(6,2)` | |
| `meeting_hours` | `decimal(6,2)` | |
| `active_percentage` | `decimal(5,2)` | Activity rate |
| `productive_app_hours` | `decimal(6,2)` | Sum of daily work-classified app/domain time |
| `focus_hours` | `decimal(6,2)` | Sum of daily deep-focus time |
| `activity_score_avg` | `decimal(5,2)` | Average monitoring-derived score |
| `work_output_score_avg` | `decimal(5,2)` | Nullable; average WorkSync output score |
| `productivity_score` | `decimal(5,2)` | Final period score |
| `productivity_score_basis` | `varchar(30)` | `composite`, `activity_only`, `worksync_only`, `insufficient_data` |
| `data_coverage_percentage` | `decimal(5,2)` | Period evidence completeness |
| `intensity_avg` | `decimal(5,2)` | |
| `exceptions_count` | `int` | |
| `trend_vs_previous_week_json` | `jsonb` | `{"active_pct_change": +5.2, "hours_change": -0.5}` |
| `created_at` | `timestamptz` | |

**Indexes:** `(tenant_id, employee_id, week_start)` UNIQUE

### `monthly_employee_report`

Monthly aggregation.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `year` | `int` | |
| `month` | `int` | 1-12 |
| `total_hours` | `decimal(7,2)` | |
| `active_hours` | `decimal(7,2)` | |
| `idle_hours` | `decimal(7,2)` | |
| `meeting_hours` | `decimal(7,2)` | |
| `active_percentage` | `decimal(5,2)` | Activity rate |
| `productive_app_hours` | `decimal(7,2)` | Sum of daily work-classified app/domain time |
| `focus_hours` | `decimal(7,2)` | Sum of daily deep-focus time |
| `activity_score_avg` | `decimal(5,2)` | Average monitoring-derived score |
| `work_output_score_avg` | `decimal(5,2)` | Nullable; average WorkSync output score |
| `productivity_score` | `decimal(5,2)` | Final period score |
| `productivity_score_basis` | `varchar(30)` | `composite`, `activity_only`, `worksync_only`, `insufficient_data` |
| `data_coverage_percentage` | `decimal(5,2)` | Period evidence completeness |
| `intensity_avg` | `decimal(5,2)` | |
| `exceptions_count` | `int` | |
| `performance_pattern_json` | `jsonb` | Weekday patterns, peak hours |
| `comparative_rank_in_department` | `int` | Rank by active% within department |
| `created_at` | `timestamptz` | |

**Indexes:** `(tenant_id, employee_id, year, month)` UNIQUE

### `monitoring_snapshot`

Tenant-wide daily metrics.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `date` | `date` | |
| `total_employees` | `int` | Active employees count |
| `active_count` | `int` | Employees with activity this day |
| `avg_active_percentage` | `decimal(5,2)` | Tenant-wide activity-rate average |
| `avg_activity_score` | `decimal(5,2)` | Tenant-wide monitoring-derived score |
| `avg_work_output_score` | `decimal(5,2)` | Nullable; employees with WorkSync output data |
| `avg_productivity_score` | `decimal(5,2)` | Tenant-wide final score |
| `avg_data_coverage_percentage` | `decimal(5,2)` | Average evidence completeness |
| `avg_meeting_percentage` | `decimal(5,2)` | |
| `total_exceptions` | `int` | Total alerts generated |
| `top_exception_types_json` | `jsonb` | Most common exception types |
| `department_breakdown_json` | `jsonb` | Per-department active% |
| `created_at` | `timestamptz` | |

**Indexes:** `(tenant_id, date)` UNIQUE

### `wms_productivity_snapshots`

Optional productivity data derived from internal WorkSync task, time, sprint, and delivery records. One row per employee per period when WorkSync modules are enabled.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `period_type` | `varchar(10)` | `daily`, `weekly`, `monthly` |
| `period_start` | `date` | Start of period |
| `period_end` | `date` | End of period |
| `tasks_completed` | `int` | Total tasks completed in period |
| `tasks_on_time` | `int` | Tasks completed by deadline |
| `on_time_delivery_rate` | `decimal(5,2)` | `(tasks_on_time / tasks_completed) * 100` |
| `work_output_score` | `decimal(5,2)` | WorkSync-computed output score (0-100) |
| `productivity_score` | `decimal(5,2)` | Deprecated alias for `work_output_score` during migration; do not use for new code |
| `active_projects_count` | `int` | Projects active during period |
| `velocity_story_points` | `int` | nullable - story points if WMS uses them |
| `submitted_at` | `timestamptz` | When WMS submitted this snapshot |
| `created_at` | `timestamptz` | |

**Indexes:** `(tenant_id, employee_id, period_type, period_start)` UNIQUE

> **Phase note:** This table is created in Phase 1 so Productivity Analytics can combine agent-based monitoring signals with internal WorkSync delivery signals when the tenant has WorkSync enabled. There is no bridge endpoint.

---

## Domain Events (intra-module - MediatR)

> These events are published and consumed within this module only. They never cross the module boundary.

| Event | Published When | Handler |
|:------|:---------------|:--------|
| _(none)_ | - | - |

## Cross-Module Events (cross-module - MediatR INotification)

### Publishes

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `DailyReportReady` | Daily report aggregation complete | [[modules/notifications/overview\|Notifications]] (send summary to managers) |
| `WeeklyReportReady` | Weekly report aggregation complete | [[modules/notifications/overview\|Notifications]] (send weekly digest) |
| `MonthlyReportReady` | Monthly report aggregation complete | [[modules/notifications/overview\|Notifications]] |

### Consumes

| Event | Source Module | Action Taken |
|:------|:-------------|:-------------|
| `ActivitySnapshotReceived` | [[modules/activity-monitoring/overview\|Activity Monitoring]] | Update real-time monitoring status feed |
| `ExceptionAlertCreated` | [[modules/exception-engine/overview\|Exception Engine]] | Increment daily exception count in monitoring snapshot |

---

## Key Business Rules

1. **Reports are pre-computed, not real-time.** Dashboard API serves pre-aggregated data from these tables.
2. **Daily reports aggregate from `activity_daily_summary` + `presence_sessions`** - never from raw snapshots.
3. **Score vocabulary is strict.** `active_percentage` is labelled "Activity rate". `activity_score` is monitoring-derived. `work_output_score` is WorkSync-derived. `productivity_score` is the final score and must expose `productivity_score_basis`.
4. **Composite score formula:** when both monitoring and WorkSync output evidence exist, compute `productivity_score = (work_output_score * 0.40) + (productive_context_score * 0.25) + (presence_reliability_score * 0.20) + (collaboration_score * 0.10) - exception_penalty`, then clamp 0-100. `data_coverage_percentage` gates confidence, not the score itself.
   - `productive_context_score` comes from work-classified app/domain time plus focus time.
   - `presence_reliability_score` comes from scheduled-vs-present time, break compliance, and data coverage.
   - `collaboration_score` comes from valid meeting time and Work Collaboration signals where enabled.
   - `exception_penalty` is 0-5 points based on unresolved severity-weighted exceptions.
5. **Fallback score:** if WorkSync output data is unavailable, populate `productivity_score_basis = activity_only` and label the UI as "Activity-derived score". Do not compare activity-only scores against composite scores in department rankings.
6. **Meeting time is valid work context.** Meetings reduce idle penalties when `meeting_detection` is enabled and the meeting session is inside a presence window. A low keyboard/mouse count during a meeting is not automatically low productivity.
7. **Comparative rankings** (department rank) are only shown to managers with `analytics:view` permission, never to the employee themselves. Rankings must compare only employees with the same `productivity_score_basis` and acceptable `data_coverage_percentage`.
8. **Export formats:** CSV and Excel via the [[modules/reporting-engine/overview|Reporting Engine]]. PDF deferred to Phase 2.
9. **Monitoring snapshot** includes ALL active employees, even those with monitoring disabled (they show presence data only, no activity breakdown).
11. **Executive dashboard** shows monitoring-level summary only. Individual employee data is not shown unless there is an escalated or critical exception alert.
12. **Manager detail view** allows drill-down for employees visible through management coverage or configured analytics/reviewer access: app usage breakdown, allowlist violations, activity timeline, WorkSync output signals, score basis, and data coverage.

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/analytics/daily/{employeeId}` | `analytics:view` | Daily report |
| GET | `/api/v1/analytics/weekly/{employeeId}` | `analytics:view` | Weekly report |
| GET | `/api/v1/analytics/monthly/{employeeId}` | `analytics:view` | Monthly report |
| GET | `/api/v1/analytics/monitoring` | `analytics:view` | Monitoring snapshot for date |
| GET | `/api/v1/analytics/trends/{employeeId}` | `analytics:view` | Trend data for charts |
| GET | `/api/v1/analytics/export/daily` | `analytics:export` | Export daily report (CSV/Excel) |
| GET | `/api/v1/analytics/export/weekly` | `analytics:export` | Export weekly report |
| GET | `/api/v1/analytics/export/monitoring` | `analytics:export` | Export monitoring snapshot |
| GET | `/api/v1/analytics/my/daily` | `analytics:view` | Employee's own daily report (self-service) |
| GET | `/api/v1/analytics/my/weekly` | `analytics:view` | Employee's own weekly report |
| GET | `/api/v1/analytics/my/monthly` | `analytics:view` | Employee's own monthly report |
| GET | `/api/v1/analytics/my/trends` | `analytics:view` | Employee's own trend data for charts |
| GET | `/api/v1/analytics/executive/summary` | `analytics:view` | Executive-level monitoring summary (exceptions only, no individual drill-down) |
| GET | `/api/v1/analytics/executive/exceptions` | `analytics:view` | Executive-level exception overview (escalated/critical only) |

---

## Hangfire Jobs

| Job | Schedule | Queue | Purpose |
|:----|:---------|:------|:--------|
| `GenerateDailyReportsJob` | Daily 11:30 PM | Default | Aggregate daily data -> `daily_employee_report` + `monitoring_snapshot` |
| `GenerateWeeklyReportsJob` | Monday 1:00 AM | Default | Aggregate week -> `weekly_employee_report` |
| `GenerateMonthlyReportsJob` | 1st of month 2:00 AM | Batch | Aggregate month -> `monthly_employee_report` |

---

## Important Notes

- **Score basis is mandatory in DTOs and exports.** Every productivity score must declare whether it is `composite`, `activity_only`, `worksync_only`, or `insufficient_data`.
- **Activity-only scores are fallback evidence.** They are useful for monitoring trends but should not be mixed with composite WorkSync-backed scores in rankings, reviews, or executive summaries.
- **This module does NOT collect data.** It only aggregates data from other modules.
- **For real-time dashboard data**, the frontend queries [[modules/time-attendance/overview|Time & Attendance]] `GetLiveMonitoringStatusAsync()` - not this module. This module serves historical/aggregated reports.
- **Performance module integration:** [[database/performance|Performance]] can pull `GetProductivityScoreAsync()` to include productivity data in performance reviews (optional, configurable by tenant). This score combines agent-based reports (`daily_employee_report`) with WorkSync output metrics (`wms_productivity_snapshots`) when available and always returns score basis.
- **Work Analytics are optional.** If the tenant has no WorkSync modules enabled, `wms_productivity_snapshots` is empty and `GetProductivityScoreAsync()` uses an activity-derived fallback. No configuration change is needed, but UI/reporting must label the basis clearly.

## Features

- [[modules/productivity-analytics/daily-reports/overview|Daily Reports]] - One row per employee per day with hours, activity rate, work-classified app time, score basis, and top apps - frontend: [[modules/productivity-analytics/daily-reports/frontend|Frontend]]
- [[modules/productivity-analytics/weekly-reports/overview|Weekly Reports]] - Weekly aggregation with trend vs prior week
- [[modules/productivity-analytics/monthly-reports/overview|Monthly Reports]] - Monthly aggregation with department comparative ranking
- [[modules/productivity-analytics/monitoring-snapshots/overview|Monitoring Snapshots]] - Tenant-wide daily metrics and per-department breakdown
- Employee Self Service - Employee-facing dashboard: own hours, activity rate, work-classified app time, score basis, and trends (`analytics:view`)
- Executive Dashboard - executive-level monitoring summary: key metrics + exceptions only (`analytics:view`)
- Manager Detail View - Manager drill-down: per-employee app usage, activity timeline, allowlist violations

---

## Related

- [[infrastructure/multi-tenancy|Multi Tenancy]] - All report tables use `(tenant_id, employee_id, date)` UNIQUE indexes
- [[security/data-classification|Data Classification]] - Department rankings only visible to managers (`analytics:view`)
- [[backend/messaging/event-catalog|Event Catalog]] - `DailyReportReady`, `WeeklyReportReady`, `MonthlyReportReady`
- [[security/compliance|Compliance]] - Monitoring snapshots cover all employees (monitoring-disabled show presence only)
- [[current-focus/DEV1-productivity-analytics|DEV1: Productivity Analytics]] - Implementation task file

See also: [[backend/module-catalog|Module Catalog]], [[modules/activity-monitoring/overview|Activity Monitoring]], [[modules/time-attendance/overview|Time & Attendance]], [[modules/exception-engine/overview|Exception Engine]], [[modules/reporting-engine/overview|Reporting Engine]]
