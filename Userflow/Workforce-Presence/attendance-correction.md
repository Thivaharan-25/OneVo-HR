# Attendance Correction

**Area:** Workforce Presence  
**Required Permission(s):** `attendance:write` (submit correction) or `attendance:approve` (approve correction)  
**Related Permissions:** `attendance:read-own` (view own sessions)

---

## Preconditions

- Presence session exists → [[presence-session-view]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Select Session to Correct
- **UI:** Workforce → Presence → select date → click session → "Request Correction"
- **API:** `GET /api/v1/workforce/presence/sessions/{id}`

### Step 2: Submit Correction
- **UI:** Show original clock-in/out → enter corrected times → select reason (forgot to clock in/out, device error, worked remotely) → add notes → submit
- **API:** `POST /api/v1/workforce/attendance-corrections`
- **Backend:** AttendanceCorrectionService.SubmitAsync() → [[attendance-corrections]]
- **DB:** `attendance_corrections` — status: "Pending"

### Step 3: Approval
- **UI:** Approver navigates to Workforce → Corrections → Pending → sees original vs corrected times → Approve/Reject
- **API:** `PUT /api/v1/workforce/attendance-corrections/{id}/approve`
- **Validation:** Approver cannot approve own corrections
- **DB:** If approved: `presence_sessions` updated, audit trail created

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Correction already pending | Blocked | "A correction is already pending for this session" |
| Corrected time outside shift | Warning | "Corrected time is outside assigned shift hours" |

## Events Triggered

- `AttendanceCorrectionRequested` → [[event-catalog]]
- `AttendanceCorrectionApproved` → [[event-catalog]]
- Notification to approver → [[notification-system]]

## Related Flows

- [[presence-session-view]]
- [[shift-schedule-setup]]

## Module References

- [[attendance-corrections]]
- [[presence-sessions]]
