# Weekly Reports — End-to-End Logic

**Module:** Productivity Analytics
**Feature:** Weekly Reports

---

## Generate Weekly Reports

### Flow

```
GenerateWeeklyReportsJob (Hangfire, Monday 1:00 AM)
  -> WeeklyReportService.GenerateAsync(tenantId, weekStart, ct)
    -> 1. Get all active employees
    -> 2. For each employee:
       -> Aggregate daily_employee_report rows for Mon-Fri
       -> Calculate: total_hours, active_hours, idle_hours, meeting_hours
       -> Calculate intensity_avg
       -> Get exception count for the week
       -> Compare with previous week: trend_vs_previous_week_json
       -> UPSERT into weekly_employee_report
    -> 3. Publish WeeklyReportReady event
```

### Key Rules

- **Weekly reports aggregate from daily reports** — never from raw data.
- **Trend comparison** shows week-over-week changes in active percentage and hours.

## Related

- [[productivity-analytics/weekly-reports/overview|Weekly Reports Overview]]
- [[productivity-analytics/daily-reports/overview|Daily Reports]]
- [[productivity-analytics/monthly-reports/overview|Monthly Reports]]
- [[error-handling]]
- [[event-catalog]]
- [[shared-kernel]]
- [[WEEK4-productivity-analytics]]
