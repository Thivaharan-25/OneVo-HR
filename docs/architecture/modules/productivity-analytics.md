# Module: Productivity Analytics

**Namespace:** `ONEVO.Modules.ProductivityAnalytics`
**Pillar:** 2 — Workforce Intelligence
**Owner:** Dev 1 (Week 4)
**Tables:** 4
**Task File:** [[WEEK4-productivity-analytics]]

---

## Purpose

Aggregates data from [[activity-monitoring]], [[workforce-presence]], and [[core-hr]] into daily/weekly/monthly reports and workforce-wide snapshots. Serves both the dashboard API and CSV/Excel export. This is the **reporting layer** for Pillar 2.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[activity-monitoring]] | `IActivityMonitoringService` | Daily summaries for aggregation |
| **Depends on** | [[workforce-presence]] | `IWorkforcePresenceService` | Attendance/hours data |
| **Depends on** | [[core-hr]] | `IEmployeeService` | Employee/department context |
| **Depends on** | [[exception-engine]] | `IExceptionEngineService` | Exception counts per day |
| **Consumed by** | [[performance]] | `IProductivityAnalyticsService` | Productivity scores for reviews |
| **Consumed by** | [[reporting-engine]] | — (via query) | Scheduled report generation |

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

## Database Tables (4)

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

---

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `DailyReportReady` | Daily report aggregation complete | [[notifications]] (send summary to managers) |
| `WeeklyReportReady` | Weekly report aggregation complete | [[notifications]] (send weekly digest) |
| `MonthlyReportReady` | Monthly report aggregation complete | [[notifications]] |

---

## Key Business Rules

1. **Reports are pre-computed, not real-time.** Dashboard API serves pre-aggregated data from these tables.
2. **Daily reports aggregate from `activity_daily_summary` + `presence_sessions`** — never from raw snapshots.
3. **Comparative rankings** (department rank) are only shown to managers with `analytics:view` permission, never to the employee themselves.
4. **Export formats:** CSV and Excel via the [[reporting-engine]]. PDF deferred to Phase 2.
5. **Workforce snapshot** includes ALL active employees, even those with monitoring disabled (they show presence data only, no activity breakdown).

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
- **For real-time dashboard data**, the frontend queries [[workforce-presence]] `GetLiveWorkforceStatusAsync()` — not this module. This module serves historical/aggregated reports.
- **Performance module integration:** [[performance]] can pull `GetProductivityScoreAsync()` to include productivity data in performance reviews (optional, configurable by tenant).

See also: [[module-catalog]], [[activity-monitoring]], [[workforce-presence]], [[exception-engine]], [[reporting-engine]]
