# Presence Session View

**Area:** Time & Attendance / Monitoring  
**Trigger:** Employee or manager views attendance log (user action - view only)
**Required Permission(s):** `attendance:read-own` (own) or `attendance:read` (others - backend applies management coverage to filter results)  
**Related Permissions:** `monitoring:view` (live dashboard)

---

## Preconditions

- Shifts/schedules assigned -> [[Userflow/Time-Attendance/shift-schedule-setup|Shift Schedule Setup]]
- Employees clocking in (via attendance/biometric device or desktop agent)
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Presence
- **UI:** Sidebar -> Time & Attendance -> Attendance. Use `Time Tracking` or `Team Attendance` inside the page depending on permission.
- **API:** `GET /api/v1/time-attendance/presence?date={today}`

### Step 2: View Sessions
- **UI:** Table/grid showing per employee: clock-in time, clock-out time (or "Active"), break time, total hours, status badge (On-time, Late, Early Departure, Absent)
- **Real-time:** Active sessions update via SignalR -> [[backend/real-time|Real-Time Architecture]]
- **Color coding:** Green = on-time, Yellow = late < 15 min, Red = late > 15 min, Grey = absent

### Step 3: Filter & Drill Down
- **API:** `GET /api/v1/time-attendance/presence/{employeeId}?date={date}`

### Step 4: Export
- **UI:** Click Export -> CSV/Excel with selected date range and filters

## Variations

### With `attendance:read-own` only
- Employee sees only their own sessions and history

### With `monitoring:view`
- Gets additional live dashboard view with real-time status grid -> [[Userflow/Monitoring/live-dashboard|Live Dashboard]]

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No schedule assigned | Employee shown as N/A | "No schedule assigned" badge |
| No permission for department | Filtered out | Only sees permitted employees |

## Events Triggered

- None (read-only flow)

## Related Flows

- [[Userflow/Time-Attendance/shift-schedule-setup|Shift Schedule Setup]]
- [[Userflow/Time-Attendance/attendance-correction|Attendance Correction]]
- [[Userflow/Monitoring/live-dashboard|Live Dashboard]]

## Module References

- [[modules/time-attendance/presence-sessions/overview|Presence Sessions]]
- [[modules/time-attendance/shifts-schedules/overview|Shifts Schedules]]
- [[backend/real-time|Real-Time Architecture]]
