# Attendance Correction

**Area:** Time & Attendance / Time & Attendance
**Trigger:** Employee, manager, or authorized admin corrects an attendance row (user action)
**Required Permission(s):** `attendance:write` (submit correction) or `attendance:approve` (approve correction)
**Related Permissions:** `attendance:read-own`, scoped `attendance:read`

---

## Preconditions

- Attendance row or presence session exists -> [[Userflow/Time-Attendance/presence-session-view|Presence Session View]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Visibility Rules

- Normal employees see and manage their own attendance.
- Managers also keep their own self-attendance view; manager status does not remove personal attendance workflows.
- Authorized users can see employee attendance only for employees returned by backend management coverage and permission checks.
- The flow is not employee-only and not manager-only.

The Attendance screen is a single operational page at `/time-attendance/attendance`. It uses an in-page segmented control:

- `Time Tracking` for every employee with own attendance access.
- `Team Attendance` only for users with employee visibility through management coverage or attendance permission.

Do not add separate sidebar items for Time Tracking, Team Attendance, or Attendance Corrections.

## Flow Steps

### Step 1: Select Attendance Row
- **UI:** Time & Attendance -> Attendance -> Time Tracking -> attendance history row -> "Request correction"
- **Manager UI:** Time & Attendance -> Attendance -> Team Attendance -> scoped employee attendance row -> "Request correction" or "Correct"
- **API:** `GET /api/v1/time-attendance/presence/{employeeId}?date={date}`

Correction actions appear at row level inside attendance history/log. Do not add a large top-level correction button.

### Step 2: Submit Correction
- **UI:** Show original clock-in/out -> enter corrected times -> select reason -> add notes -> submit
- **Correction reasons:** Forgot to clock in, Forgot to clock out, Wrong clock-in time, Wrong clock-out time, Break missing/wrong, Full-day attendance issue, Other attendance issue. Do not include work area change - use Work Area Change Request instead.
- **API:** `POST /api/v1/time-attendance/attendance-corrections`
- **Backend:** AttendanceCorrectionService.SubmitAsync() -> [[modules/time-attendance/attendance-corrections/overview|Attendance Corrections]]
- **DB:** `attendance_corrections` - status: "Pending" unless policy allows direct admin correction

### Step 3: Approval
- **UI:** Approver opens pending corrections -> sees original vs corrected times -> Approve/Reject
- **API:** `PUT /api/v1/time-attendance/attendance-corrections/{id}/approve`
- **Validation:** Approval routes to one eligible owner through management coverage. Approver cannot approve own corrections unless a specific policy allows self-approval.
- **DB:** If approved: `presence_sessions` or attendance records updated, audit trail created

## Clock-in Policy Dependency

Clock-in Policy defines:

- Who must clock in.
- Date-effective policy ranges.
- Onsite/remote verification behavior that affects whether a correction is needed.
- Progressive late Time Off deduction rules.

When a correction changes the clock-in time, the system must recalculate late minutes and any late deduction that was applied. If the original clock-in triggered a late Time Off deduction, the correction approval flow should reverse the original deduction and apply the corrected deduction (or no deduction if the corrected time is on time). Both the reversal and the new deduction create balance audit entries.

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Correction already pending | Blocked | "A correction is already pending for this session" |
| Corrected time outside assigned schedule | Warning or policy validation | "Corrected time is outside assigned schedule hours" |
| User outside allowed coverage | Blocked | "You do not have access to correct this employee's attendance" |
| No eligible owner for approval | Routing issue created | "No eligible owner could approve this request. Check position coverage and permissions." |

## Events Triggered

- `AttendanceCorrectionRequested` -> [[backend/messaging/event-catalog|Event Catalog]]
- `AttendanceCorrectionApproved` -> [[backend/messaging/event-catalog|Event Catalog]]
- Notification to approver -> [[backend/notification-system|Notification System]]

## Related Flows

- [[Userflow/Time-Attendance/presence-session-view|Presence Session View]]
- [[Userflow/Time-Attendance/shift-schedule-setup|Shift Schedule Setup]]

## Module References

- [[modules/time-attendance/attendance-corrections/overview|Attendance Corrections]]
- [[modules/time-attendance/presence-sessions/overview|Presence Sessions]]
