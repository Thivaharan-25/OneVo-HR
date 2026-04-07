# WEEK4: Productivity Analytics + Reporting Engine

**Status:** Planned
**Priority:** High
**Assignee:** Dev 1
**Sprint:** Week 4 (Apr 28 – May 2)
**Module:** ProductivityAnalytics + ReportingEngine

## Description

Implement daily/weekly/monthly employee reports, workforce snapshots, trend analysis, and the reporting engine serving both HR and workforce intelligence reports with CSV/Excel export.

## Acceptance Criteria

### Productivity Analytics
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

### Reporting Engine
- [ ] `report_definitions` table — configurable with cron schedule
- [ ] Report types: `headcount`, `turnover`, `leave_utilization`, `productivity_daily`, `productivity_weekly`, `workforce_summary`, `exception_summary`
- [ ] `report_executions` table — execution log
- [ ] `report_templates` table — column definitions + default filters
- [ ] On-demand and scheduled report execution via Hangfire
- [ ] CSV export
- [ ] Excel (xlsx) export
- [ ] Generated reports stored via `IFileService`
- [ ] Unit tests ≥80% coverage

## Related

- [[productivity-analytics]] — module architecture
- [[reporting-engine]] — reporting engine architecture
- [[activity-monitoring]] — activity_daily_summary is primary data source
- [[workforce-presence]] — presence_sessions is primary data source
- [[exception-engine]] — exception counts included in exception_summary report type
- [[multi-tenancy]] — tenant-scoped reports and configurable report definitions
- [[WEEK3-activity-monitoring]] — activity_daily_summary aggregated here
- [[WEEK2-workforce-presence-setup]] — presence_sessions aggregated here
- [[WEEK4-exception-engine]] — exception_summary report type reads IExceptionEngineService
- [[WEEK3-performance]] — productivity_score fed into performance reviews from IProductivityAnalyticsService
- [[WEEK4-supporting-bridges]] — notifications deliver DailyReportReady / WeeklyReportReady events
