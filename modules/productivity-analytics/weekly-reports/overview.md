# Weekly Reports

**Module:** Productivity Analytics  
**Feature:** Weekly Reports

---

## Purpose

Weekly aggregation with trend comparison to previous week.

## Database Tables

### `weekly_employee_report`
Key columns: `employee_id`, `week_start` (Monday), `total_hours`, `active_hours`, `idle_hours`, `meeting_hours`, `active_percentage`, `intensity_avg`, `exceptions_count`, `trend_vs_previous_week_json`.

## Hangfire Jobs

| Job | Schedule | Purpose |
|:----|:---------|:--------|
| `GenerateWeeklyReportsJob` | Monday 1:00 AM | Aggregate week |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/analytics/weekly/{employeeId}` | `analytics:view` | Weekly report |
| GET | `/api/v1/analytics/export/weekly` | `analytics:export` | Export |

## Related

- [[productivity-analytics|Productivity Analytics Module]]
- [[productivity-analytics/daily-reports/overview|Daily Reports]]
- [[productivity-analytics/monthly-reports/overview|Monthly Reports]]
- [[productivity-analytics/workforce-snapshots/overview|Workforce Snapshots]]
- [[multi-tenancy]]
- [[auth-architecture]]
- [[event-catalog]]
- [[shared-kernel]]
- [[WEEK4-productivity-analytics]]
