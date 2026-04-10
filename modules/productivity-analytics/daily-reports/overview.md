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
| `DailyReportReady` | Aggregation complete | [[modules/notifications/overview\|Notifications]] |

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

- [[modules/productivity-analytics/overview|Productivity Analytics Module]]
- [[frontend/architecture/overview|Weekly Reports]]
- [[frontend/architecture/overview|Monthly Reports]]
- [[frontend/architecture/overview|Workforce Snapshots]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[security/data-classification|Data Classification]]
- [[backend/shared-kernel|Shared Kernel]]
- [[current-focus/DEV1-productivity-analytics|DEV1: Productivity Analytics]]
