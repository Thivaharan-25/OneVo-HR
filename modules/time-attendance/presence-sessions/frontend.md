# Page: Monitoring Dashboard

**Route:** `/monitoring`
**Permission:** `monitoring:view`
**Real-time:** SignalR `monitoring-live` channel

## Purpose

Real-time overview of the entire monitoring - who's active, idle, on Time Off, absent. The primary monitoring command center.

## Layout

```
+-------------------------------------------------------------+
| PageHeader: "Live Monitoring" + "Last updated: 5s ago"       |
+----------+----------+----------+----------+----------------+
| Total    | Active   | Idle     | On Time Off | Absent         |
| 487      | 342 ^5   | 89       | 41       | 15             |
|          | (70.2%)  | (18.3%)  | (8.4%)   | (3.1%)         |
+----------+----------+----------+----------+----------------+
|                                                             |
|  [Department Breakdown - Horizontal Bar Chart]              |
|  Engineering ################---- 82%                       |
|  Sales       ##############------ 71%                       |
|  Support     ############-------- 65%                       |
|                                                             |
+---------------------------------+---------------------------+
| Activity Heatmap (hourly grid)  | Active Exceptions (list)  |
|                                 | [critical] Critical: 2    |
|                                 | [warning] Warning: 5      |
|                                 | [info] Info: 12           |
|                                 |                           |
|                                 | [View All ->]              |
+---------------------------------+---------------------------+
| Employee List (filterable, sortable)                        |
| +------+--------+--------+----------+---------+----------+ |
| | Name | Dept   | Status | Active % | Top App | Actions  | |
| +------+--------+--------+----------+---------+----------+ |
| | J.D. | Eng    | [active] | 85%      | VS Code | [View]   | |
| | M.K. | Sales  | [idle]   | 45%      | Chrome  | [View]   | |
| +------+--------+--------+----------+---------+----------+ |
| [Search] [Filter: Department v] [Filter: Status v]         |
+-------------------------------------------------------------+
```

## Data Sources

| Component | API | Refresh |
|:----------|:----|:--------|
| KPI Cards | `GET /api/v1/monitoring/live` | SignalR `monitoring-live` |
| Department Bar | Same endpoint | SignalR |
| Activity Heatmap | `GET /analytics/monitoring?date=today` | 5 min polling |
| Monitoring Alerts Panel | `GET /monitoring/alerts?status=new` | Notifications `notifications-{userId}` |
| Employee List | `GET /api/v1/time-attendance/presence?date=today` | SignalR |

## Interactions

- Click employee row -> navigate to `/monitoring/employees/{employeeId}`
- Click exception -> navigate to `/monitoring/exceptions` with alert ID
- Filter by department, status, search by name
- KPI cards show trend arrows (vs yesterday)

## Empty States

- **Monitoring disabled:** "Monitoring is not enabled for your organization. Contact your admin."
- **No employees online:** "No employees are currently active."
- **No exceptions:** "No active exceptions. All clear!" (with checkmark icon)

## Related

- [[modules/time-attendance/presence-sessions/overview|Presence Sessions Overview]]
- [[modules/time-attendance/presence-sessions/end-to-end-logic|Presence Sessions - End-to-End Logic]]
- [[security/auth-architecture|Auth Architecture]]
- [[security/data-classification|Data Classification]]
