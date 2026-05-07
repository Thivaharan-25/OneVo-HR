# Live Workforce Dashboard

**Area:** Workforce Intelligence  
**Trigger:** Manager opens real-time workforce view (user action — view only)
**Required Permission(s):** `workforce:view`  
**Related Permissions:** `workforce:manage` (take actions), `attendance:read-team` (team-scoped)

---

## Preconditions

- Monitoring enabled → [[Userflow/Workforce-Intelligence/monitoring-configuration|Monitoring Configuration]]
- Desktop agents deployed → [[Userflow/Workforce-Intelligence/agent-deployment|Agent Deployment]]
- Employees have active presence sessions
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Open Dashboard
- **UI:** Sidebar → Workforce → Live Dashboard

### Tabs Within Live Dashboard

| Tab | Content | Previously |
|:----|:--------|:-----------|
| Overview | Real-time employee grid, summary stats | Live Dashboard |
| Activity | Activity snapshots, app usage | Separate sidebar item "Activity" |
| Work Insights | Productivity metrics, trends | Separate sidebar item "Productivity" |
| Online Status | Presence tracking, status dots | Separate sidebar item "Presence" |
- **API:** `GET /api/v1/workforce/live`
- **Real-time:** SignalR connection on `workforce-live` channel → [[backend/real-time|Real-Time Architecture]]

### Step 2: View Real-Time Grid
- **UI:** Grid showing all monitored employees:
  - Name, department, team
  - Status: Active (green), Idle (yellow), Away (orange), Offline (grey)
  - Current app/window title
  - Session duration today
  - Work-classified app time today
  - Activity rate and data coverage today
- Updates every few seconds via SignalR

### Step 3: Filter & Sort
- **UI rule:** Use activity rate, work-classified app time, idle time, and data coverage for sorting. Do not label raw active time as productivity.
- **UI:** Filter by: department, team, status → sort by: name, activity rate, work-classified app time, idle time, data coverage → search by employee name

### Step 4: Drill Down
- **UI rule:** Show activity-derived score, score basis, data coverage, and attendance status. Only show final productivity score when Productivity Analytics provides a comparable score basis.
- **UI:** Click employee → detail panel: full timeline (apps, breaks, screenshots if enabled), productivity score, attendance status
- Links: [[Userflow/Workforce-Intelligence/activity-snapshot-view|Activity Snapshot View]]

### Step 5: Summary Stats
- **UI rule:** Use average activity rate, average work-classified app time, and data coverage. Avoid "top productive department" unless the metric is a composite productivity score with comparable basis.
- **UI:** Top bar: total active now, total idle, total offline, avg activity rate, avg work-classified app time, avg data coverage

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

- [[Userflow/Workforce-Intelligence/monitoring-configuration|Monitoring Configuration]]
- [[Userflow/Workforce-Intelligence/activity-snapshot-view|Activity Snapshot View]]
- [[Userflow/Workforce-Presence/presence-session-view|Presence Session View]]
- [[Userflow/Exception-Engine/exception-dashboard|Alerts Overview]]

## Module References

- [[modules/workforce-presence/presence-sessions/overview|Presence Sessions]]
- [[modules/activity-monitoring/overview|Activity Monitoring]]
- [[backend/real-time|Real-Time Architecture]]
- [[backend/monitoring-data-flow|Monitoring Data Flow]]
