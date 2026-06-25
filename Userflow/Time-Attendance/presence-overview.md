# Time & Attendance - Overview

**Area:** Monitoring -> Live Status (`/monitoring`)  
**Trigger:** User clicks the Monitoring navigation item, or navigates to `/monitoring`  
**Required Permission:** `monitoring:view`

## Purpose

The Live Status screen is the default landing for the Monitoring module. It shows a live card grid of all employees the user has access to see. Each card combines three data points - online status, productivity score, and current task - so managers can understand who is working and how effectively without switching between tabs or views.

If Phase 1 lightweight monitoring/attendance alerts or the desktop agent detect a problem with an employee (missed punch, anomaly, biometric mismatch), that employee's card is escalated: a red alert banner appears on the card and it is sorted to the top of the grid.


## Time & Attendance Boundary

Attendance self-service, team attendance, corrections, schedules, clock-in policy, and overtime rules belong under `Time & Attendance`. Monitoring keeps live operational visibility, alerts, and device/activity review as a first-class top-level module.
## Card Anatomy

```
+------------------------------------------+
| [critical] AGENT ALERT: Missed clock-in 09:00 |  <- alert banner (only when flagged)
+------------------------------------------+
|  [Avatar]  Sarah Johnson                 |
|            Senior Engineer   o Online    |  <- name, position, online status dot
|  Productivity  ########--  82%          |  <- weekly productivity score
|  Now: "Fix login redirect bug"           |  <- current assigned task (from WMS)
+------------------------------------------+
```

**Card data sources:**
| Card Element | Source Module |
|---|---|
| Online status dot (o) | time-attendance |
| Productivity % | productivity-analytics |
| Current task text | WMS task module (active `TASK` assigned to this user) |
| Alert banner | lightweight monitoring/attendance alerts + agent-gateway |

**Online status dot colours:**
- Green o - Clocked in and active
- Amber o - On break
- Grey o - Offline / not clocked in
- Red o - Exception flagged

## Card Sort Order

1. Agent-flagged cards - sorted to top, ordered by exception severity (critical -> high -> medium)
2. Online employees - sorted alphabetically
3. On-break employees
4. Offline employees

## Flow Steps

1. User opens Monitoring - default route is `/monitoring`
2. System loads all employees in the current company tenant scope that the user has `monitoring:view` access to
3. Cards render in sort order (flagged first, then online, then break, then offline)
4. Live updates stream via SignalR - presence status and productivity scores update without page refresh
5. User clicks any card -> navigates to `/monitoring/employees/[employeeId]` (Employee Activity Detail)

## Filtering and Search

- Search bar filters cards by employee name or position
- Department filter (dropdown) - narrows to employees within a department
- Status filter - show only: Online / On Break / Offline / Flagged

## Related Flows

- [[Userflow/Time-Attendance/employee-activity-detail|Employee Activity Detail]]
- [[Userflow/Work-Management/wm-overview|WMS Overview]]
- [[Userflow/Work-Management/resource-flow|Resource Management]]
