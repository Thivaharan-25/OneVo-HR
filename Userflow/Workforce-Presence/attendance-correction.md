# Attendance Correction

**Area:** Workforce Presence  
**Required Permission(s):** `attendance:write` (submit correction) or `attendance:approve` (approve correction)  
**Related Permissions:** `attendance:read-own` (view own sessions)

---

## Preconditions

- Presence session exists → [[Userflow/Workforce-Presence/presence-session-view|Presence Session View]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Select Session to Correct
- **UI:** Workforce → Presence → select date → click session → "Request Correction"
- **API:** `GET /api/v1/workforce/presence/sessions/{id}`

### Step 2: Submit Correction
- **UI:** Show original clock-in/out → enter corrected times → select reason (forgot to clock in/out, device error, worked remotely) → add notes → submit
- **API:** `POST /api/v1/workforce/attendance-corrections`
- **Backend:** AttendanceCorrectionService.SubmitAsync() → [[modules/workforce-presence/attendance-corrections/overview|Attendance Corrections]]
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

- `AttendanceCorrectionRequested` → [[backend/messaging/event-catalog|Event Catalog]]
- `AttendanceCorrectionApproved` → [[backend/messaging/event-catalog|Event Catalog]]
- Notification to approver → [[backend/notification-system|Notification System]]

## Related Flows

- [[Userflow/Workforce-Presence/presence-session-view|Presence Session View]]
- [[Userflow/Workforce-Presence/shift-schedule-setup|Shift Schedule Setup]]

## Module References

- [[modules/workforce-presence/attendance-corrections/overview|Attendance Corrections]]
- [[modules/workforce-presence/presence-sessions/overview|Presence Sessions]]
