# Device Sessions - End-to-End Logic

**Module:** Time & Attendance
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
GET /api/v1/monitoring/device-sessions/{employeeId}?date=2026-04-05
  -> DeviceSessionController.Get(employeeId, date)
    -> [RequirePermission("monitoring:view")]
    -> TimeAttendanceService.GetDeviceSessionsAsync(employeeId, date, ct)
      -> Query device_sessions WHERE employee_id AND session_start date range
      -> Return Result.Success(sessionDtos)
```

## Related

- [[modules/time-attendance/device-sessions/overview|Device Sessions Overview]]
- [[modules/time-attendance/presence-sessions/overview|Presence Sessions]]
- [[Userflow/Time-Attendance/break-tracking|Break Tracking]]
- [[modules/time-attendance/attendance-corrections/overview|Attendance Corrections]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
