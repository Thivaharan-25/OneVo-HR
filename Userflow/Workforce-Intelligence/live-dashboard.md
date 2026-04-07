# Live Workforce Dashboard

**Area:** Workforce Intelligence  
**Required Permission(s):** `workforce:view`  
**Related Permissions:** `workforce:manage` (take actions), `attendance:read-team` (team-scoped)

---

## Preconditions

- Monitoring enabled → [[monitoring-configuration]]
- Desktop agents deployed → [[agent-deployment]]
- Employees have active presence sessions
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Open Dashboard
- **UI:** Sidebar → Workforce → Live Dashboard
- **API:** `GET /api/v1/workforce/live`
- **Real-time:** SignalR connection on `workforce-live` channel → [[real-time]]

### Step 2: View Real-Time Grid
- **UI:** Grid showing all monitored employees:
  - Name, department, team
  - Status: Active (green), Idle (yellow), Away (orange), Offline (grey)
  - Current app/window title
  - Session duration today
  - Productive hours today
- Updates every few seconds via SignalR

### Step 3: Filter & Sort
- **UI:** Filter by: department, team, status → sort by: name, productive hours, idle time → search by employee name

### Step 4: Drill Down
- **UI:** Click employee → detail panel: full timeline (apps, breaks, screenshots if enabled), productivity score, attendance status
- Links: [[activity-snapshot-view]]

### Step 5: Summary Stats
- **UI:** Top bar: total active now, total idle, total offline, avg productive hours, top productive department

## Variations

### Team-scoped view
- With `attendance:read-team` only: sees only direct reports / team members

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No agents online | Empty grid | "No employees currently online" |
| SignalR disconnected | Stale data warning | "Live updates paused — reconnecting..." |

## Events Triggered

- None (read-only, real-time view)

## Related Flows

- [[monitoring-configuration]]
- [[activity-snapshot-view]]
- [[presence-session-view]]
- [[exception-dashboard]]

## Module References

- [[presence-sessions]]
- [[activity-monitoring]]
- [[real-time]]
- [[monitoring-data-flow]]
