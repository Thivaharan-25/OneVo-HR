# Workforce Presence — Overview

**Area:** Workforce → Presence (`/workforce`)  
**Trigger:** User clicks the Workforce pillar icon, or navigates to `/workforce`  
**Required Permission:** `workforce:read`

## Purpose

The Presence screen is the default landing for the Workforce pillar. It shows a live card grid of all employees the user has access to see. Each card combines three data points — online status, productivity score, and current task — so managers can understand who is working and how effectively without switching between tabs or views.

If the exception engine or desktop agent detects a problem with an employee (missed punch, anomaly, biometric mismatch), that employee's card is escalated: a red alert banner appears on the card and it is sorted to the top of the grid.

## Card Anatomy

```
┌──────────────────────────────────────────┐
│ 🔴 AGENT ALERT: Missed clock-in 09:00   │  ← alert banner (only when flagged)
├──────────────────────────────────────────┤
│  [Avatar]  Sarah Johnson                 │
│            Senior Engineer   ● Online    │  ← name, job title, online status dot
│  Productivity  ████████░░  82%          │  ← weekly productivity score
│  Now: "Fix login redirect bug"           │  ← current assigned task (from WMS)
└──────────────────────────────────────────┘
```

**Card data sources:**
| Card Element | Source Module |
|---|---|
| Online status dot (●) | workforce-presence |
| Productivity % | productivity-analytics |
| Current task text | WMS task module (active `TASK` assigned to this user) |
| Alert banner | exception-engine + agent-gateway |

**Online status dot colours:**
- Green ● — Clocked in and active
- Amber ● — On break
- Grey ● — Offline / not clocked in
- Red ● — Exception flagged

## Card Sort Order

1. Agent-flagged cards — sorted to top, ordered by exception severity (critical → high → medium)
2. Online employees — sorted alphabetically
3. On-break employees
4. Offline employees

## Flow Steps

1. User opens Workforce pillar — default route is `/workforce`
2. System loads all employees in the entity scope that the user has `workforce:read` access to
3. Cards render in sort order (flagged first, then online, then break, then offline)
4. Live updates stream via SignalR — presence status and productivity scores update without page refresh
5. User clicks any card → navigates to `/workforce/[employeeId]` (Employee Activity Detail)

## Filtering and Search

- Search bar filters cards by employee name or job title
- Department filter (dropdown) — narrows to employees within a department
- Status filter — show only: Online / On Break / Offline / Flagged

## Related Flows

- [[Userflow/Workforce-Presence/employee-activity-detail|Employee Activity Detail]]
- [[Userflow/Work-Management/wm-overview|WMS Overview]]
- [[Userflow/Work-Management/resource-flow|Resource Management]]
