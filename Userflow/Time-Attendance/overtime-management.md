# Overtime Management

**Area:** Time & Attendance / Time & Attendance
**Trigger:** Employee requests overtime, manager submits for a team member, or system detects overtime hours (user action or system-triggered)
**Required Permission(s):** `attendance:write` (request) or `attendance:approve` (approve)
**Related Permissions:** `payroll:read` (view overtime in payroll)

---

## Preconditions

- Employee has assigned schedule -> [[Userflow/Time-Attendance/shift-schedule-setup|Shift Schedule Setup]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]
- Overtime rules exist under Time & Attendance -> Overtime Rules.

## Flow Steps

### Step 1: Request Overtime
- **UI:** Time & Attendance -> Attendance row/action or allowed overtime action -> select date -> enter duration -> select reason -> submit
- **API:** `POST /api/v1/time-attendance/overtime`
- **Backend:** OvertimeService.RequestAsync() -> [[modules/time-attendance/overtime/overview|Overtime]]
- **DB:** `overtime_records` - status: "Pending"

Overtime request is an operational request tied to the employee's attendance, assigned schedule, date, duration, reason, and Overtime Rules.

### Step 2: Approval
- **UI:** The one eligible owner resolved through Org Structure management coverage sees the overtime request in Inbox -> reviews against assigned schedule, attendance records, and overtime policy -> Approve/Reject
- **API:** `PUT /api/v1/time-attendance/overtime/{id}/approve`
- **DB:** If approved: overtime hours recorded, status: "Approved"

### Step 3: Payroll Integration
- **Backend:** Approved overtime hours feed into next payroll run and use configured overtime rate rules.
- Links to: [[Userflow/Payroll/payroll-run-execution|Payroll Run Execution]]

## Variations

### Auto-detected overtime
- When employee clocks out after scheduled end time or total scheduled hours are exceeded, the system can auto-calculate potential overtime. Approval is still required unless Overtime Rules explicitly allow no approval.

### Overtime Rules fields
- Applies to: Full company, Departments, Positions, Employees.
- Overtime requires approval: Yes/No.
- Overtime approver: Management coverage owner.
- Minimum overtime duration: minutes.
- Overtime starts after: scheduled end time or total scheduled hours exceeded.
- Allow employee request: Yes/No.
- Allow manager submit for team member: Yes/No.

Phase 1 overtime approval does not use the workflow/automation engine. Full configurable workflow/automation remains Phase 2.

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No schedule assigned | Cannot calculate | "Assign a work schedule first" |
| Duplicate date request | Blocked | "Overtime already requested for this date" |
| Overtime outside policy range | Validation fails or requires approval exception | "Overtime is outside the allowed policy" |

## Events Triggered

- `OvertimeRequested` -> [[backend/messaging/event-catalog|Event Catalog]]
- `OvertimeApproved` -> [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Time-Attendance/shift-schedule-setup|Shift Schedule Setup]]
- [[Userflow/Time-Attendance/presence-session-view|Presence Session View]]
- [[Userflow/Payroll/payroll-run-execution|Payroll Run Execution]]

## Module References

- [[modules/time-attendance/overtime/overview|Overtime]]
- [[modules/time-attendance/shifts-schedules/overview|Shifts Schedules]]
