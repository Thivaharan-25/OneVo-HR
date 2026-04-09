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

- [[modules/productivity-analytics/overview|Productivity Analytics Module]]
- [[frontend/architecture/overview|Daily Reports]]
- [[frontend/architecture/overview|Weekly Reports]]
- [[frontend/architecture/overview|Workforce Snapshots]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[security/data-classification|Data Classification]]
- [[backend/shared-kernel|Shared Kernel]]
- [[current-focus/DEV1-productivity-analytics|DEV1: Productivity Analytics]]
