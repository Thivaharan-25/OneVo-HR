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

- [[modules/productivity-analytics/overview|Productivity Analytics Module]]
- [[frontend/architecture/overview|Daily Reports]]
- [[frontend/architecture/overview|Weekly Reports]]
- [[frontend/architecture/overview|Monthly Reports]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[security/data-classification|Data Classification]]
- [[backend/shared-kernel|Shared Kernel]]
- [[current-focus/DEV1-productivity-analytics|DEV1: Productivity Analytics]]
