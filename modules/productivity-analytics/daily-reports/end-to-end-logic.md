# Daily Reports — End-to-End Logic

**Module:** Productivity Analytics
**Feature:** Daily Reports

---

## Generate Daily Reports

### Flow

```
GenerateDailyReportsJob (Hangfire, daily 11:30 PM)
  -> DailyReportService.GenerateAsync(tenantId, date, ct)
    -> 1. Get all active employees for tenant
    -> 2. For each employee:
       -> a. Get activity summary: IActivityMonitoringService.GetDailySummaryAsync()
       -> b. Get presence data: IWorkforcePresenceService.GetPresenceForDateAsync()
       -> c. Get exception count: IExceptionEngineService.GetExceptionCountAsync()
       -> d. Compute:
          -> total_hours from presence sessions
          -> active_hours, idle_hours, meeting_hours from activity summary
          -> intensity_score from activity summary
          -> top_apps_json from activity summary
          -> device_split_json from device tracking
       -> e. UPSERT into daily_employee_report
    -> 3. Generate workforce_snapshot for the day:
       -> Aggregate across all employees
       -> avg_active_percentage, total_exceptions, department_breakdown
       -> UPSERT into workforce_snapshot
    -> 4. Publish DailyReportReady event
```

## Get Daily Report (API)

### Flow

```
GET /api/v1/analytics/daily/{employeeId}?date=2026-04-05
  -> AnalyticsController.GetDaily(employeeId, date)
    -> [RequirePermission("analytics:view")]
    -> ProductivityAnalyticsService.GetDailyReportAsync(employeeId, date, ct)
      -> Query daily_employee_report WHERE employee_id AND date
      -> Return Result.Success(reportDto)

```

## Related

- [[productivity-analytics/daily-reports/overview|Daily Reports Overview]]
- [[productivity-analytics/weekly-reports/overview|Weekly Reports]]
- [[productivity-analytics/workforce-snapshots/overview|Workforce Snapshots]]
- [[error-handling]]
- [[event-catalog]]
- [[shared-kernel]]
- [[WEEK4-productivity-analytics]]
