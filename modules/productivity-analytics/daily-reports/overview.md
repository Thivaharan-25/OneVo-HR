# Daily Reports

**Module:** Productivity Analytics  
**Feature:** Daily Reports

---

## Purpose

One row per employee per day. Aggregated from `activity_daily_summary` + `presence_sessions`.

## Database Tables

### `daily_employee_report`
Key columns: `employee_id`, `date`, `total_hours`, `active_hours`, `idle_hours`, `meeting_hours`, `active_percentage`, `top_apps_json`, `intensity_score`, `device_split_json`, `exceptions_count`, `anomaly_flags_json`.

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `DailyReportReady` | Aggregation complete | [[notifications]] |

## Hangfire Jobs

| Job | Schedule | Purpose |
|:----|:---------|:--------|
| `GenerateDailyReportsJob` | Daily 11:30 PM | Aggregate daily data |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/analytics/daily/{employeeId}` | `analytics:view` | Daily report |
| GET | `/api/v1/analytics/export/daily` | `analytics:export` | Export CSV/Excel |

## Related

- [[productivity-analytics|Productivity Analytics Module]]
- [[productivity-analytics/weekly-reports/overview|Weekly Reports]]
- [[productivity-analytics/monthly-reports/overview|Monthly Reports]]
- [[productivity-analytics/workforce-snapshots/overview|Workforce Snapshots]]
- [[multi-tenancy]]
- [[auth-architecture]]
- [[event-catalog]]
- [[data-classification]]
- [[shared-kernel]]
- [[WEEK4-productivity-analytics]]
