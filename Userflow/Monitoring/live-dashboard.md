# Live Monitoring Dashboard

**Area:** Monitoring
**Trigger:** Manager opens real-time monitoring view (user action - view only)
**Required Permission(s):** `monitoring:view`  

---

## Preconditions

- Monitoring enabled -> [[Userflow/Monitoring/monitoring-configuration|Monitoring Configuration]]
- Desktop agents deployed -> [[Userflow/Monitoring/agent-deployment|Agent Deployment]]
- Employees have active presence sessions
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Open Dashboard
- **UI:** Sidebar -> Monitoring

### Tabs Within Live Dashboard

| Tab | Content | Previously |
|:----|:--------|:-----------|
| Overview | Real-time employee grid, summary stats | Live Dashboard |
| Activity | Activity snapshots, app usage | Separate sidebar item "Activity" |
| Work Insights | Productivity metrics, trends | Separate sidebar item "Productivity" |
| Online Status | Presence tracking, status dots | Separate sidebar item "Presence" |
- **API:** `GET /api/v1/monitoring/live`
- **Real-time:** SignalR connection on `monitoring-live` channel -> [[backend/real-time|Real-Time Architecture]]

### Step 2: View Real-Time Grid
- **UI:** Grid showing all monitored employees:
  - Status: Active (green), Idle (yellow), Away (orange), Offline (grey)
  - Current app/window title
  - Session duration today
  - Work-classified app time today
  - Activity rate and data coverage today
- Updates every few seconds via SignalR

### Step 3: Filter & Sort
- **UI rule:** Use activity rate, work-classified app time, idle time, and data coverage for sorting. Do not label raw active time as productivity.

### Step 4: Drill Down
- **UI rule:** Show activity-derived score, score basis, data coverage, and attendance status. Only show final productivity score when Productivity Analytics provides a comparable score basis.
- **UI:** Click employee -> detail panel: full timeline (apps, breaks, screenshots if enabled), productivity score, attendance status
- Links: [[Userflow/Monitoring/activity-snapshot-view|Activity Snapshot View]]

### Step 5: Summary Stats
- **UI rule:** Use average activity rate, average work-classified app time, and data coverage. Avoid "top productive department" unless the metric is a composite productivity score with comparable basis.
- **UI:** Top bar: total active now, total idle, total offline, avg activity rate, avg work-classified app time, avg data coverage

## Variations


## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No agents online | Empty grid | "No employees currently online" |
| SignalR disconnected | Stale data warning | "Live updates paused - reconnecting..." |

## Events Triggered

- None (read-only, real-time view)

## Related Flows

- [[Userflow/Monitoring/monitoring-configuration|Monitoring Configuration]]
- [[Userflow/Monitoring/activity-snapshot-view|Activity Snapshot View]]
- [[Userflow/Time-Attendance/presence-session-view|Presence Session View]]
- [[Userflow/Exception-Engine/exception-dashboard|Alerts Overview]]

## Module References

- [[modules/time-attendance/presence-sessions/overview|Presence Sessions]]
- [[modules/activity-monitoring/overview|Activity Monitoring]]
- [[backend/real-time|Real-Time Architecture]]
- [[backend/monitoring-data-flow|Monitoring Data Flow]]
