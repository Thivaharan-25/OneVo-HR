# Employee Activity Detail

**Area:** Workforce → Presence → Employee (`/workforce/[employeeId]`)  
**Trigger:** User clicks an employee card on the Presence screen  
**Required Permission:** `workforce:read` (view); `activity:read:team` (view another employee's activity)

## Purpose

The activity detail screen shows what a specific employee has been working on. It is the drill-down from their presence card. The screen combines time logs, task activity, and productivity analytics into a single filterable timeline — replacing the old Activity tab.

## Layout

```
← Back to Presence                                  [Link: View People Profile]

[Avatar] Sarah Johnson — Senior Engineer   ● Online
Productivity this week: ████████░░ 82%    Exception: None

──────────────────────────────────────────
Filters: [Date Range ▾]  [Task ▾]  [Project ▾]
──────────────────────────────────────────

Activity Timeline
─────────────────
09:15  Logged 45min on "Fix login redirect bug"        [Project: Auth Revamp]
10:02  Status changed: In Progress → In Review         [Task: Fix login redirect bug]
11:30  Added comment on "API timeout investigation"    [Project: Backend Stability]
13:00  Clock-in resumed after lunch break
14:15  Logged 1h 10min on "Write unit tests for auth"  [Project: Auth Revamp]
```

## Data Sources

| Section | Source |
|---|---|
| Online status, break/clock events | workforce-presence module |
| Productivity score | productivity-analytics module |
| Time logs | WMS time module (`TIME_LOG`) |
| Task status changes | WMS activity log (`ACTIVITY_LOG`) |
| Comments | WMS collab module (`COMMENT`) |
| Exception history | exception-engine |

## Flow Steps

1. User clicks an employee card on the Presence screen
2. System navigates to `/workforce/[employeeId]`
3. System loads: employee summary (name, title, status, productivity score), activity timeline for the current day
4. Timeline shows events in reverse-chronological order: time logs, task status changes, comments, clock events
5. User applies filters:
   - **Date Range** — select a custom range or preset (today / this week / last 7 days / this month)
   - **Task** — filter timeline to events for a specific task
   - **Project** — filter timeline to events for a specific project
6. Filtered timeline re-renders immediately
7. User clicks "View People Profile" → navigates to `/people/employees/[employeeId]`

## Exception History

If the employee has active or recent exceptions (from the exception-engine), an "Exceptions" section appears below the summary:
- Lists each exception: type, timestamp, severity, resolution status
- Exceptions sourced from the exception-engine module

## Related Flows

- [[Userflow/Workforce-Presence/presence-overview|Workforce Presence]]
- [[Userflow/Work-Management/task-flow|Task Management]]
- [[Userflow/Work-Management/time-tracking-flow|Time Tracking]]
