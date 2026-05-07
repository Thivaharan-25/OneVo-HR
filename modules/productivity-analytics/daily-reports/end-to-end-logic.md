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
       -> d. Get WorkSync output snapshot for employee/date if WorkSync is enabled
       -> e. Compute:
          -> total_hours from presence sessions
          -> active_hours, idle_hours, meeting_hours from activity summary
          -> productive_app_hours, focus_hours, activity_score, data_coverage_percentage from activity summary
          -> work_output_score from wms_productivity_snapshots when available
          -> productivity_score and productivity_score_basis:
             -> composite when activity + WorkSync output evidence are both available
             -> activity_only when WorkSync output evidence is unavailable
             -> worksync_only when monitoring is disabled but WorkSync output evidence exists
             -> insufficient_data when coverage is below tenant threshold
          -> intensity_score from activity summary
          -> top_apps_json from activity summary
          -> device_split_json from device tracking
       -> f. UPSERT into daily_employee_report
    -> 3. Generate workforce_snapshot for the day:
       -> Aggregate across all employees
       -> avg_active_percentage, avg_activity_score, avg_work_output_score,
          avg_productivity_score, avg_data_coverage_percentage,
          total_exceptions, department_breakdown
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

- [[frontend/architecture/overview|Daily Reports Overview]]
- [[frontend/architecture/overview|Weekly Reports]]
- [[frontend/architecture/overview|Workforce Snapshots]]
- [[backend/messaging/error-handling|Error Handling]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/shared-kernel|Shared Kernel]]
- [[current-focus/DEV1-productivity-analytics|DEV1: Productivity Analytics]]
