# Presence Session View

**Area:** Workforce Presence  
**Required Permission(s):** `attendance:read-own` (own) or `attendance:read` (all) or `attendance:read-team` (team)  
**Related Permissions:** `workforce:view` (live dashboard)

---

## Preconditions

- Shifts/schedules assigned → [[shift-schedule-setup]]
- Employees clocking in (via biometric device or desktop agent)
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Presence
- **UI:** Sidebar → Workforce → Presence → today's view by default
- **API:** `GET /api/v1/workforce/presence/sessions?date={today}`

### Step 2: View Sessions
- **UI:** Table/grid showing per employee: clock-in time, clock-out time (or "Active"), break time, total hours, status badge (On-time, Late, Early Leave, Absent)
- **Real-time:** Active sessions update via SignalR → [[real-time]]
- **Color coding:** Green = on-time, Yellow = late < 15 min, Red = late > 15 min, Grey = absent

### Step 3: Filter & Drill Down
- **UI:** Filter by: date range, department, team, status → click employee row → detailed session view: timeline with clock-in, breaks, clock-out, total productive time
- **API:** `GET /api/v1/workforce/presence/sessions/{id}`

### Step 4: Export
- **UI:** Click Export → CSV/Excel with selected date range and filters

## Variations

### With `attendance:read-own` only
- Employee sees only their own sessions and history

### With `workforce:view`
- Gets additional live dashboard view with real-time status grid → [[live-dashboard]]

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No schedule assigned | Employee shown as N/A | "No schedule assigned" badge |
| No permission for department | Filtered out | Only sees permitted employees |

## Events Triggered

- None (read-only flow)

## Related Flows

- [[shift-schedule-setup]]
- [[attendance-correction]]
- [[live-dashboard]]

## Module References

- [[presence-sessions]]
- [[shifts-schedules]]
- [[real-time]]
