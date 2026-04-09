# Task: Productivity Analytics + Reporting Engine

**Assignee:** Dev 1
**Module:** ProductivityAnalytics + ReportingEngine
**Priority:** High
**Dependencies:** [[current-focus/DEV3-activity-monitoring|DEV3 Activity Monitoring]] (activity_daily_summary), [[current-focus/DEV3-workforce-presence-setup|DEV3 Workforce Presence Setup]] (presence_sessions)

---

## Step 1: Backend

### Acceptance Criteria

#### Productivity Analytics
- [ ] `daily_employee_report` table — one row/employee/day
- [ ] Aggregate from `activity_daily_summary` + `presence_sessions` (never raw snapshots)
- [ ] `weekly_employee_report` table — weekly aggregation with trend vs previous week
- [ ] `monthly_employee_report` table — monthly with performance patterns + department rank
- [ ] `workforce_snapshot` table — tenant-wide daily metrics
- [ ] `GenerateDailyReportsJob` (daily 11:30 PM)
- [ ] `GenerateWeeklyReportsJob` (Monday 1:00 AM)
- [ ] `GenerateMonthlyReportsJob` (1st of month 2:00 AM)
- [ ] Department ranking: comparative_rank_in_department by active%
- [ ] `IProductivityAnalyticsService` public interface implementation
- [ ] Domain events: `DailyReportReady`, `WeeklyReportReady`, `MonthlyReportReady`

#### Reporting Engine
- [ ] `report_definitions` table — configurable with cron schedule
- [ ] Report types: `headcount`, `turnover`, `leave_utilization`, `productivity_daily`, `productivity_weekly`, `workforce_summary`, `exception_summary`
- [ ] `report_executions` table — execution log
- [ ] `report_templates` table — column definitions + default filters
- [ ] On-demand and scheduled report execution via Hangfire
- [ ] CSV export
- [ ] Excel (xlsx) export
- [ ] Generated reports stored via `IFileService`
- [ ] Unit tests >= 80% coverage

### Backend References

- [[modules/productivity-analytics/overview|productivity-analytics]] — module architecture
- [[modules/reporting-engine/overview|reporting-engine]] — reporting engine architecture
- [[modules/activity-monitoring/overview|activity-monitoring]] — activity_daily_summary is primary data source
- [[modules/workforce-presence/overview|workforce-presence]] — presence_sessions is primary data source
- [[infrastructure/multi-tenancy|Multi Tenancy]] — tenant-scoped reports

---

## Step 2: Frontend

### Pages to Build

```
app/(dashboard)/workforce/productivity/
├── page.tsx                      # Team productivity dashboard
├── trends/page.tsx               # Historical trends
├── apps/page.tsx                 # Application usage breakdown
├── components/                   # Colocated feature components
│   ├── ProductivityChart.tsx     # Productivity metrics chart (active %, idle %)
│   ├── TrendSparkline.tsx        # Mini trend lines per employee (vs previous period)
│   └── AppUsageBreakdown.tsx     # Categorized app usage table
└── _types.ts                     # Local TypeScript definitions

app/(dashboard)/reports/
├── page.tsx                      # Report library
├── builder/page.tsx              # Report builder
├── [id]/page.tsx                 # Report result / download
├── components/                   # Colocated feature components
│   ├── ReportBuilder.tsx         # Drag-and-drop report config
│   └── ReportScheduleForm.tsx    # Schedule recurring reports
└── _types.ts                     # Local TypeScript definitions
```

### What to Build

- [ ] Productivity dashboard page (ProductivityChart):
  - Toggle: daily / weekly / monthly view
  - Employee DataTable with productivity metrics (active %, idle %, app usage breakdown)
  - TrendSparkline per employee (vs previous period)
  - Department ranking column
  - Filter by department, team, date range
- [ ] Workforce snapshot widget on dashboard (total active, idle, absent, on leave counts)
- [ ] Report builder page (ReportBuilder):
  - Select report type from templates
  - Configure filters (date range, department, team)
  - Schedule recurring reports (cron)
  - View execution history
- [ ] CSV/Excel export buttons on all report views
- [ ] Scheduled report management (list, edit, delete schedules)

### Userflows

- [[Userflow/Analytics-Reporting/productivity-dashboard|Productivity Dashboard]] — view productivity metrics and trends
- [[Userflow/Analytics-Reporting/report-creation|Report Creation]] — create and run custom reports
- [[Userflow/Analytics-Reporting/scheduled-report-setup|Scheduled Report Setup]] — schedule recurring reports
- [[Userflow/Analytics-Reporting/data-export|Data Export]] — export reports to CSV/Excel
- [[Userflow/Analytics-Reporting/workforce-snapshot|Workforce Snapshot]] — tenant-wide workforce overview

### API Endpoints (Frontend Consumes)

| Method | Endpoint | Purpose |
|:-------|:---------|:--------|
| GET | `/api/v1/analytics/daily?date={date}` | Daily employee reports |
| GET | `/api/v1/analytics/weekly?week={week}` | Weekly employee reports |
| GET | `/api/v1/analytics/monthly?month={month}` | Monthly employee reports |
| GET | `/api/v1/analytics/snapshot` | Workforce snapshot |
| GET | `/api/v1/reports/definitions` | List report definitions |
| POST | `/api/v1/reports/definitions` | Create report definition |
| POST | `/api/v1/reports/execute/{definitionId}` | Run report on-demand |
| GET | `/api/v1/reports/executions` | Report execution history |
| GET | `/api/v1/reports/executions/{id}/download` | Download report file |

### Frontend References

- [[frontend/design-system/components/component-catalog|Component Catalog]] — DataTable, StatCard, DateRangePicker
- [[frontend/design-system/patterns/data-visualization|Data Visualization]] — charts, sparklines, heatmaps
- [[frontend/data-layer/api-integration|API Integration]] — API client pattern

---

## Related Tasks

- [[current-focus/DEV3-activity-monitoring|DEV3 Activity Monitoring]] — activity_daily_summary aggregated here
- [[current-focus/DEV3-workforce-presence-setup|DEV3 Workforce Presence Setup]] — presence_sessions aggregated here
- [[current-focus/DEV2-exception-engine|DEV2 Exception Engine]] — exception_summary report type reads IExceptionEngineService
- Performance — deferred to Phase 2 (productivity_score fed into performance reviews)
- [[current-focus/DEV2-notifications|DEV2 Notifications]] — notifications deliver report-ready events
