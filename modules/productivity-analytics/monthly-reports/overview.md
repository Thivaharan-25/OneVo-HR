# Monthly Reports

**Module:** Productivity Analytics  
**Feature:** Monthly Reports

---

## Purpose

Monthly aggregation with performance patterns, peak hours, and comparative department ranking.

## Database Tables

### `monthly_employee_report`
Key columns: `employee_id`, `year`, `month`, `total_hours`, `active_hours`, `intensity_avg`, `performance_pattern_json`, `comparative_rank_in_department`.

## Key Business Rules

1. Comparative rankings only shown to managers with `analytics:view`, never to the employee.

## Hangfire Jobs

| Job | Schedule | Purpose |
|:----|:---------|:--------|
| `GenerateMonthlyReportsJob` | 1st of month 2:00 AM | Aggregate month |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/analytics/monthly/{employeeId}` | `analytics:view` | Monthly report |

## Related

- [[productivity-analytics|Productivity Analytics Module]]
- [[productivity-analytics/daily-reports/overview|Daily Reports]]
- [[productivity-analytics/weekly-reports/overview|Weekly Reports]]
- [[productivity-analytics/workforce-snapshots/overview|Workforce Snapshots]]
- [[multi-tenancy]]
- [[auth-architecture]]
- [[event-catalog]]
- [[data-classification]]
- [[shared-kernel]]
- [[WEEK4-productivity-analytics]]
