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

- [[modules/productivity-analytics/overview|Productivity Analytics Module]]
- [[frontend/architecture/overview|Daily Reports]]
- [[frontend/architecture/overview|Monthly Reports]]
- [[frontend/architecture/overview|Workforce Snapshots]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/shared-kernel|Shared Kernel]]
- [[current-focus/DEV1-productivity-analytics|DEV1: Productivity Analytics]]
