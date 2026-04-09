# Overtime Management

**Area:** Workforce Presence  
**Required Permission(s):** `attendance:write` (request) or `attendance:approve` (approve)  
**Related Permissions:** `payroll:read` (view overtime in payroll)

---

## Preconditions

- Employee has assigned shift/schedule → [[Userflow/Workforce-Presence/shift-schedule-setup|Shift Schedule Setup]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Request Overtime
- **UI:** Workforce → Overtime → "Request Overtime" → select date → enter expected extra hours → select reason → submit
- **API:** `POST /api/v1/workforce/overtime`
- **Backend:** OvertimeService.RequestAsync() → [[modules/workforce-presence/overtime/overview|Overtime]]
- **DB:** `overtime_requests` — status: "Pending"

### Step 2: Approval
- **UI:** Approver sees overtime request → reviews against shift schedule → Approve/Reject
- **API:** `PUT /api/v1/workforce/overtime/{id}/approve`
- **DB:** If approved: overtime hours recorded, status: "Approved"

### Step 3: Payroll Integration
- **Backend:** Approved overtime hours feed into next payroll run → calculated at overtime rate (1.5x or 2x as configured)
- Links to: [[Userflow/Payroll/payroll-run-execution|Payroll Run Execution]]

## Variations

### Auto-detected overtime
- When employee clocks out after shift end → system auto-calculates overtime → still requires approval

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No shift assigned | Cannot calculate | "Assign a shift schedule first" |
| Duplicate date request | Blocked | "Overtime already requested for this date" |

## Events Triggered

- `OvertimeRequested` → [[backend/messaging/event-catalog|Event Catalog]]
- `OvertimeApproved` → [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Workforce-Presence/shift-schedule-setup|Shift Schedule Setup]]
- [[Userflow/Workforce-Presence/presence-session-view|Presence Session View]]
- [[Userflow/Payroll/payroll-run-execution|Payroll Run Execution]]

## Module References

- [[modules/workforce-presence/overtime/overview|Overtime]]
- [[modules/workforce-presence/shifts-schedules/overview|Shifts Schedules]]
