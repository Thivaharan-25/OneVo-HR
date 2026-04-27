# Module: Productivity Analytics

**Feature Folder:** `Application/Features/ProductivityAnalytics`
**Phase:** 1 — Build
**Pillar:** 2 — Workforce Intelligence
**Owner:** Dev 1 (Week 4)
**Tables:** 5
**Task File:** [[current-focus/DEV1-productivity-analytics|DEV1: Productivity Analytics]]

---

## Purpose

Aggregates data from [[modules/activity-monitoring/overview|Activity Monitoring]], [[modules/workforce-presence/overview|Workforce Presence]], and [[modules/core-hr/overview|Core Hr]] into daily/weekly/monthly reports and workforce-wide snapshots. Serves both the dashboard API and CSV/Excel export. This is the **reporting layer** for Pillar 2.

**Three dashboard views:**
1. **Manager Dashboard** — full team visibility, drill-down per employee, exception alerts, app usage micro-management
2. **CEO Dashboard** — high-level workforce summary, exception-only escalation, no individual drill-down unless flagged
3. **Employee Self-Service** — own data only (hours, active %, app usage, trends). Cannot see other employees.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[modules/activity-monitoring/overview\|Activity Monitoring]] | `IActivityMonitoringService` | Daily summaries for aggregation |
| **Depends on** | [[modules/workforce-presence/overview\|Workforce Presence]] | `IWorkforcePresenceService` | Attendance/hours data |
| **Depends on** | [[modules/core-hr/overview\|Core Hr]] | `IEmployeeService` | Employee/department context |
| **Depends on** | [[modules/exception-engine/overview\|Exception Engine]] | `IExceptionEngineService` | Exception counts per day |
| **Depends on** | WMS Bridge | `POST /api/v1/bridges/productivity-metrics/snapshots` | Inbound task completion + productivity scores from WorkManage Pro |
| **Consumed by** | [[database/performance\|Performance]] | `IProductivityAnalyticsService` | Productivity scores for reviews |
| **Consumed by** | [[modules/reporting-engine/overview\|Reporting Engine]] | — (via query) | Scheduled report generation |

---

## Public Interface

```csharp
// ONEVO.Modules.ProductivityAnalytics/Public/IProductivityAnalyticsService.cs
public interface IProductivityAnalyticsService
{
    Task<Result<DailyEmployeeReportDto>> GetDailyReportAsync(Guid employeeId, DateOnly date, CancellationToken ct);
    Task<Result<WeeklyEmployeeReportDto>> GetWeeklyReportAsync(Guid employeeId, DateOnly weekStart, CancellationToken ct);
    Task<Result<MonthlyEmployeeReportDto>> GetMonthlyReportAsync(Guid employeeId, int year, int month, CancellationToken ct);
    Task<Result<WorkforceSnapshotDto>> GetWorkforceSnapshotAsync(DateOnly date, CancellationToken ct);
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
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `date` | `date` | |
| `total_hours` | `decimal(5,2)` | From presence sessions |
| `active_hours` | `decimal(5,2)` | From activity summaries |
| `idle_hours` | `decimal(5,2)` | |
| `meeting_hours` | `decimal(5,2)` | |
| `active_percentage` | `decimal(5,2)` | |
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
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `week_start` | `date` | Monday of the week |
| `total_hours` | `decimal(6,2)` | |
| `active_hours` | `decimal(6,2)` | |
| `idle_hours` | `decimal(6,2)` | |
| `meeting_hours` | `decimal(6,2)` | |
| `active_percentage` | `decimal(5,2)` | |
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
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `year` | `int` | |
| `month` | `int` | 1–12 |
| `total_hours` | `decimal(7,2)` | |
| `active_hours` | `decimal(7,2)` | |
| `idle_hours` | `decimal(7,2)` | |
| `meeting_hours` | `decimal(7,2)` | |
| `active_percentage` | `decimal(5,2)` | |
| `intensity_avg` | `decimal(5,2)` | |
| `exceptions_count` | `int` | |
| `performance_pattern_json` | `jsonb` | Weekday patterns, peak hours |
| `comparative_rank_in_department` | `int` | Rank by active% within department |
| `created_at` | `timestamptz` | |

**Indexes:** `(tenant_id, employee_id, year, month)` UNIQUE

### `workforce_snapshot`

Tenant-wide daily metrics.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `date` | `date` | |
| `total_employees` | `int` | Active employees count |
| `active_count` | `int` | Employees with activity this day |
| `avg_active_percentage` | `decimal(5,2)` | Tenant-wide average |
| `avg_meeting_percentage` | `decimal(5,2)` | |
| `total_exceptions` | `int` | Total alerts generated |
| `top_exception_types_json` | `jsonb` | Most common exception types |
| `department_breakdown_json` | `jsonb` | Per-department active% |
| `created_at` | `timestamptz` | |

**Indexes:** `(tenant_id, date)` UNIQUE

### `wms_productivity_snapshots`

Inbound productivity data from WorkManage Pro (Phase 2 bridge). One row per employee per period.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `period_type` | `varchar(10)` | `daily`, `weekly`, `monthly` |
| `period_start` | `date` | Start of period |
| `period_end` | `date` | End of period |
| `tasks_completed` | `int` | Total tasks completed in period |
| `tasks_on_time` | `int` | Tasks completed by deadline |
| `on_time_delivery_rate` | `decimal(5,2)` | `(tasks_on_time / tasks_completed) * 100` |
| `productivity_score` | `decimal(5,2)` | WMS-computed composite score (0–100) |
| `active_projects_count` | `int` | Projects active during period |
| `velocity_story_points` | `int` | nullable — story points if WMS uses them |
| `submitted_at` | `timestamptz` | When WMS submitted this snapshot |
| `created_at` | `timestamptz` | |

**Indexes:** `(tenant_id, employee_id, period_type, period_start)` UNIQUE

> **Phase note:** This table is created in Phase 1 so the bridge can start receiving WMS data immediately. The Performance module (Phase 2) reads it via `IProductivityAnalyticsService.GetProductivityScoreAsync()` which combines agent-based scores with this WMS data.

---

## Domain Events (intra-module — MediatR)

> These events are published and consumed within this module only. They never leave the module.

| Event | Published When | Handler |
|:------|:---------------|:--------|
| _(none)_ | — | — |

## Integration Events (cross-module — RabbitMQ)

### Publishes

| Event | Routing Key | Published When | Consumers |
|:------|:-----------|:---------------|:----------|
| `DailyReportReady` | `analytics.daily` | Daily report aggregation complete | [[modules/notifications/overview\|Notifications]] (send summary to managers) |
| `WeeklyReportReady` | `analytics.weekly` | Weekly report aggregation complete | [[modules/notifications/overview\|Notifications]] (send weekly digest) |
| `MonthlyReportReady` | `analytics.monthly` | Monthly report aggregation complete | [[modules/notifications/overview\|Notifications]] |

### Consumes

| Event | Routing Key | Source Module | Action Taken |
|:------|:-----------|:-------------|:-------------|
| `ActivitySnapshotReceived` | `activity.snapshot` | [[modules/activity-monitoring/overview\|Activity Monitoring]] | Update real-time workforce status feed |
| `ExceptionAlertCreated` | `exception.alert` | [[modules/exception-engine/overview\|Exception Engine]] | Increment daily exception count in workforce snapshot |

---

## Key Business Rules

1. **Reports are pre-computed, not real-time.** Dashboard API serves pre-aggregated data from these tables.
2. **Daily reports aggregate from `activity_daily_summary` + `presence_sessions`** — never from raw snapshots.
3. **Comparative rankings** (department rank) are only shown to managers with `analytics:view` permission, never to the employee themselves.
4. **Export formats:** CSV and Excel via the [[modules/reporting-engine/overview|Reporting Engine]]. PDF deferred to Phase 2.
5. **Workforce snapshot** includes ALL active employees, even those with monitoring disabled (they show presence data only, no activity breakdown).
6. **Employee self-service dashboard** uses `analytics:view:self` permission — employee can ONLY see their own data. No access to team/department aggregates. No comparative rankings. Shows: daily hours, active %, app usage breakdown, meeting time, weekly/monthly trends.
7. **CEO dashboard** uses `analytics:view:ceo` permission — shows workforce-level summary only. Individual employee data is NOT shown unless they have an escalated/critical exception alert. Designed to avoid information overload — key metrics + exceptions only.
8. **Manager micro-management view** — managers with `analytics:view` can drill into any employee in their hierarchy: full app usage breakdown, per-app time, allowlist violations, activity timeline. This enables the "micro manage everyone about app usage" requirement.

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/analytics/daily/{employeeId}` | `analytics:view` | Daily report |
| GET | `/api/v1/analytics/weekly/{employeeId}` | `analytics:view` | Weekly report |
| GET | `/api/v1/analytics/monthly/{employeeId}` | `analytics:view` | Monthly report |
| GET | `/api/v1/analytics/workforce` | `analytics:view` | Workforce snapshot for date |
| GET | `/api/v1/analytics/trends/{employeeId}` | `analytics:view` | Trend data for charts |
| GET | `/api/v1/analytics/export/daily` | `analytics:export` | Export daily report (CSV/Excel) |
| GET | `/api/v1/analytics/export/weekly` | `analytics:export` | Export weekly report |
| GET | `/api/v1/analytics/export/workforce` | `analytics:export` | Export workforce snapshot |
| GET | `/api/v1/analytics/my/daily` | `analytics:view:self` | Employee's own daily report (self-service) |
| GET | `/api/v1/analytics/my/weekly` | `analytics:view:self` | Employee's own weekly report |
| GET | `/api/v1/analytics/my/monthly` | `analytics:view:self` | Employee's own monthly report |
| GET | `/api/v1/analytics/my/trends` | `analytics:view:self` | Employee's own trend data for charts |
| GET | `/api/v1/analytics/ceo/summary` | `analytics:view:ceo` | CEO-level workforce summary (exceptions only, no individual drill-down) |
| GET | `/api/v1/analytics/ceo/exceptions` | `analytics:view:ceo` | CEO-level exception overview (escalated/critical only) |

---

## Hangfire Jobs

| Job | Schedule | Queue | Purpose |
|:----|:---------|:------|:--------|
| `GenerateDailyReportsJob` | Daily 11:30 PM | Default | Aggregate daily data → `daily_employee_report` + `workforce_snapshot` |
| `GenerateWeeklyReportsJob` | Monday 1:00 AM | Default | Aggregate week → `weekly_employee_report` |
| `GenerateMonthlyReportsJob` | 1st of month 2:00 AM | Batch | Aggregate month → `monthly_employee_report` |

---

## Important Notes

- **This module does NOT collect data.** It only aggregates data from other modules.
- **For real-time dashboard data**, the frontend queries [[modules/workforce-presence/overview|Workforce Presence]] `GetLiveWorkforceStatusAsync()` — not this module. This module serves historical/aggregated reports.
- **Performance module integration:** [[database/performance|Performance]] can pull `GetProductivityScoreAsync()` to include productivity data in performance reviews (optional, configurable by tenant). This score combines agent-based reports (`daily_employee_report`) with WMS task data (`wms_productivity_snapshots`) when available.
- **WMS bridge is optional.** If the tenant has no WMS integration, `wms_productivity_snapshots` is empty and `GetProductivityScoreAsync()` uses agent-based data only. No configuration change needed — the service handles the null case gracefully.

## Features

- [[modules/productivity-analytics/daily-reports/overview|Daily Reports]] — One row per employee per day with hours, active %, top apps — frontend: [[modules/productivity-analytics/daily-reports/frontend|Frontend]]
- [[modules/productivity-analytics/weekly-reports/overview|Weekly Reports]] — Weekly aggregation with trend vs prior week
- [[modules/productivity-analytics/monthly-reports/overview|Monthly Reports]] — Monthly aggregation with department comparative ranking
- [[modules/productivity-analytics/workforce-snapshots/overview|Workforce Snapshots]] — Tenant-wide daily metrics and per-department breakdown
- Employee Self Service — Employee-facing dashboard: own hours, active %, app usage, trends (`analytics:view:self`)
- Ceo Dashboard — CEO-level workforce summary: key metrics + exceptions only (`analytics:view:ceo`)
- Manager Detail View — Manager drill-down: per-employee app usage, activity timeline, allowlist violations

---

## Related

- [[infrastructure/multi-tenancy|Multi Tenancy]] — All report tables use `(tenant_id, employee_id, date)` UNIQUE indexes
- [[security/data-classification|Data Classification]] — Department rankings only visible to managers (`analytics:view`)
- [[backend/messaging/event-catalog|Event Catalog]] — `DailyReportReady`, `WeeklyReportReady`, `MonthlyReportReady`
- [[security/compliance|Compliance]] — Workforce snapshots cover all employees (monitoring-disabled show presence only)
- [[current-focus/DEV1-productivity-analytics|DEV1: Productivity Analytics]] — Implementation task file

See also: [[backend/module-catalog|Module Catalog]], [[modules/activity-monitoring/overview|Activity Monitoring]], [[modules/workforce-presence/overview|Workforce Presence]], [[modules/exception-engine/overview|Exception Engine]], [[modules/reporting-engine/overview|Reporting Engine]]
