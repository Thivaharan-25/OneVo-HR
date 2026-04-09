# Device Sessions — End-to-End Logic

**Module:** Workforce Presence
**Feature:** Device Sessions

---

## Process Device Session Data

### Flow

```
Agent Gateway routes device_session data from ingest payload:
  -> DeviceSessionService.ProcessAsync(payload, ct)
    -> 1. Validate employee_id is linked to device
    -> 2. INSERT into device_sessions
       -> session_start, session_end (null if ongoing)
       -> active_minutes, idle_minutes
       -> active_percentage computed
    -> 3. If idle_minutes > threshold (from tenant settings, default 15 min):
       -> Auto-create break_record (auto_detected = true)
```

## Get Device Sessions

### Flow

```
GET /api/v1/workforce/device-sessions/{employeeId}?date=2026-04-05
  -> DeviceSessionController.Get(employeeId, date)
    -> [RequirePermission("workforce:view")]
    -> WorkforcePresenceService.GetDeviceSessionsAsync(employeeId, date, ct)
      -> Query device_sessions WHERE employee_id AND session_start date range
      -> Return Result.Success(sessionDtos)
```

## Related

- [[modules/workforce-presence/device-sessions/overview|Device Sessions Overview]]
- [[modules/workforce-presence/presence-sessions/overview|Presence Sessions]]
- [[Userflow/Workforce-Presence/break-tracking|Break Tracking]]
- [[modules/workforce-presence/attendance-corrections/overview|Attendance Corrections]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
