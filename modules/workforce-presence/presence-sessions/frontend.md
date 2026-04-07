# Page: Live Workforce Dashboard

**Route:** `/workforce/live`
**Permission:** `workforce:view`
**Real-time:** SignalR `workforce-live` channel

## Purpose

Real-time overview of the entire workforce — who's active, idle, on leave, absent. The primary monitoring command center.

## Layout

```
┌─────────────────────────────────────────────────────────────┐
│ PageHeader: "Live Workforce" + "Last updated: 5s ago"       │
├──────────┬──────────┬──────────┬──────────┬────────────────┤
│ Total    │ Active   │ Idle     │ On Leave │ Absent         │
│ 487      │ 342 ↑5   │ 89       │ 41       │ 15             │
│          │ (70.2%)  │ (18.3%)  │ (8.4%)   │ (3.1%)         │
├──────────┴──────────┴──────────┴──────────┴────────────────┤
│                                                             │
│  [Department Breakdown - Horizontal Bar Chart]              │
│  Engineering ████████████████░░░░ 82%                       │
│  Sales       ██████████████░░░░░░ 71%                       │
│  Support     ████████████░░░░░░░░ 65%                       │
│                                                             │
├─────────────────────────────────┬───────────────────────────┤
│ Activity Heatmap (hourly grid)  │ Active Exceptions (list)  │
│                                 │ 🔴 Critical: 2           │
│                                 │ 🟡 Warning: 5            │
│                                 │ 🔵 Info: 12              │
│                                 │                           │
│                                 │ [View All →]              │
├─────────────────────────────────┴───────────────────────────┤
│ Employee List (filterable, sortable)                        │
│ ┌──────┬────────┬────────┬──────────┬─────────┬──────────┐ │
│ │ Name │ Dept   │ Status │ Active % │ Top App │ Actions  │ │
│ ├──────┼────────┼────────┼──────────┼─────────┼──────────┤ │
│ │ J.D. │ Eng    │ 🟢     │ 85%      │ VS Code │ [View]   │ │
│ │ M.K. │ Sales  │ 🟡     │ 45%      │ Chrome  │ [View]   │ │
│ └──────┴────────┴────────┴──────────┴─────────┴──────────┘ │
│ [Search] [Filter: Department ▼] [Filter: Status ▼]         │
└─────────────────────────────────────────────────────────────┘
```

## Data Sources

| Component | API | Refresh |
|:----------|:----|:--------|
| KPI Cards | `GET /workforce/presence/live` | SignalR `workforce-live` |
| Department Bar | Same endpoint | SignalR |
| Activity Heatmap | `GET /analytics/workforce?date=today` | 5 min polling |
| Exceptions Panel | `GET /exceptions/alerts?status=new` | SignalR `exception-alerts` |
| Employee List | `GET /workforce/presence?date=today` | SignalR |

## Interactions

- Click employee row → navigate to `/workforce/activity/{employeeId}`
- Click exception → navigate to `/workforce/exceptions` with alert ID
- Filter by department, status, search by name
- KPI cards show trend arrows (vs yesterday)

## Empty States

- **Monitoring disabled:** "Workforce monitoring is not enabled for your organization. Contact your admin."
- **No employees online:** "No employees are currently active."
- **No exceptions:** "No active exceptions. All clear!" (with checkmark icon)

## Related

- [[presence-sessions|Presence Sessions Overview]]
- [[presence-sessions/end-to-end-logic|Presence Sessions — End-to-End Logic]]
- [[auth-architecture]]
- [[data-classification]]
