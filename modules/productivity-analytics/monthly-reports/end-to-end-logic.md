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
       -> Calculate activity_score_avg, work_output_score_avg, productivity_score,
          productivity_score_basis, and data_coverage_percentage
       -> Analyze performance_pattern_json:
          -> Which weekdays have strongest activity/output patterns
          -> Peak hours analysis
       -> Calculate comparative_rank_in_department:
          -> Rank by productivity_score only among employees with the same
             productivity_score_basis and acceptable data coverage
       -> UPSERT into monthly_employee_report
    -> 3. Publish MonthlyReportReady event
```

### Key Rules

- **Department ranking is only visible to managers** with `analytics:view` permission, never to the employee.
- **Department rank is not based on raw active percentage.** Use `productivity_score` only when score basis and coverage are comparable.
- **Monthly reports include pattern analysis** — weekday and hourly activity/output patterns.

## Related

- [[frontend/architecture/overview|Monthly Reports Overview]]
- [[frontend/architecture/overview|Weekly Reports]]
- [[frontend/architecture/overview|Daily Reports]]
- [[backend/messaging/error-handling|Error Handling]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/shared-kernel|Shared Kernel]]
- [[current-focus/DEV1-productivity-analytics|DEV1: Productivity Analytics]]
