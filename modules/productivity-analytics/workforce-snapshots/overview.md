# Workforce Snapshots

**Module:** Productivity Analytics  
**Feature:** Workforce Snapshots

---

## Purpose

Tenant-wide daily metrics including all active employees (even those with monitoring disabled — they show presence data only).

## Database Tables

### `workforce_snapshot`
Key columns: `date`, `total_employees`, `active_count`, `avg_active_percentage`, `avg_meeting_percentage`, `total_exceptions`, `top_exception_types_json`, `department_breakdown_json`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/analytics/workforce` | `analytics:view` | Workforce snapshot |
| GET | `/api/v1/analytics/trends/{employeeId}` | `analytics:view` | Trend data |
| GET | `/api/v1/analytics/export/workforce` | `analytics:export` | Export |

## Related

- [[productivity-analytics|Productivity Analytics Module]]
- [[productivity-analytics/daily-reports/overview|Daily Reports]]
- [[productivity-analytics/weekly-reports/overview|Weekly Reports]]
- [[productivity-analytics/monthly-reports/overview|Monthly Reports]]
- [[multi-tenancy]]
- [[auth-architecture]]
- [[data-classification]]
- [[shared-kernel]]
- [[WEEK4-productivity-analytics]]
