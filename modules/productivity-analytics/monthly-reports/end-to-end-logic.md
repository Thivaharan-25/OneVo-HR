# Monthly Reports — End-to-End Logic

**Module:** Productivity Analytics
**Feature:** Monthly Reports

---

## Generate Monthly Reports

### Flow

```
GenerateMonthlyReportsJob (Hangfire, 1st of month 2:00 AM)
  -> MonthlyReportService.GenerateAsync(tenantId, year, month, ct)
    -> 1. Get all active employees
    -> 2. For each employee:
       -> Aggregate daily_employee_report rows for the month
       -> Calculate all summary metrics
       -> Analyze performance_pattern_json:
          -> Which weekdays are most productive
          -> Peak hours analysis
       -> Calculate comparative_rank_in_department:
          -> Rank by active_percentage within department
       -> UPSERT into monthly_employee_report
    -> 3. Publish MonthlyReportReady event
```

### Key Rules

- **Department ranking is only visible to managers** with `analytics:view` permission, never to the employee.
- **Monthly reports include pattern analysis** — weekday and hourly productivity patterns.

## Related

- [[productivity-analytics/monthly-reports/overview|Monthly Reports Overview]]
- [[productivity-analytics/weekly-reports/overview|Weekly Reports]]
- [[productivity-analytics/daily-reports/overview|Daily Reports]]
- [[error-handling]]
- [[event-catalog]]
- [[shared-kernel]]
- [[WEEK4-productivity-analytics]]
