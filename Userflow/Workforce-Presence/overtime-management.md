# Overtime Management

**Area:** Workforce Presence  
**Required Permission(s):** `attendance:write` (request) or `attendance:approve` (approve)  
**Related Permissions:** `payroll:read` (view overtime in payroll)

---

## Preconditions

- Employee has assigned shift/schedule → [[shift-schedule-setup]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Request Overtime
- **UI:** Workforce → Overtime → "Request Overtime" → select date → enter expected extra hours → select reason → submit
- **API:** `POST /api/v1/workforce/overtime`
- **Backend:** OvertimeService.RequestAsync() → [[overtime]]
- **DB:** `overtime_requests` — status: "Pending"

### Step 2: Approval
- **UI:** Approver sees overtime request → reviews against shift schedule → Approve/Reject
- **API:** `PUT /api/v1/workforce/overtime/{id}/approve`
- **DB:** If approved: overtime hours recorded, status: "Approved"

### Step 3: Payroll Integration
- **Backend:** Approved overtime hours feed into next payroll run → calculated at overtime rate (1.5x or 2x as configured)
- Links to: [[payroll-run-execution]]

## Variations

### Auto-detected overtime
- When employee clocks out after shift end → system auto-calculates overtime → still requires approval

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No shift assigned | Cannot calculate | "Assign a shift schedule first" |
| Duplicate date request | Blocked | "Overtime already requested for this date" |

## Events Triggered

- `OvertimeRequested` → [[event-catalog]]
- `OvertimeApproved` → [[event-catalog]]

## Related Flows

- [[shift-schedule-setup]]
- [[presence-session-view]]
- [[payroll-run-execution]]

## Module References

- [[overtime]]
- [[shifts-schedules]]
