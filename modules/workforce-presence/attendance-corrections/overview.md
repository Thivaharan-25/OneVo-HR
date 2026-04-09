# Attendance Corrections

**Module:** Workforce Presence  
**Feature:** Attendance Corrections

---

## Purpose

Manager corrections to attendance data with audit trail.

## Database Tables

### `attendance_records`
Legacy clock-in/out records (biometric source).

### `attendance_corrections`
Manager corrections to attendance data.

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `AttendanceCorrected` | Manager corrects | Audit trail |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| POST | `/api/v1/workforce/corrections` | `attendance:write` | Submit correction |

## Related

- [[modules/workforce-presence/overview|Workforce Presence Module]]
- [[modules/workforce-presence/presence-sessions/overview|Presence Sessions]]
- [[modules/workforce-presence/device-sessions/overview|Device Sessions]]
- [[modules/workforce-presence/overtime/overview|Overtime]]
- [[Userflow/Workforce-Presence/break-tracking|Break Tracking]]
- [[modules/workforce-presence/shifts-schedules/overview|Shifts Schedules]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[backend/messaging/error-handling|Error Handling]]
- [[code-standards/logging-standards|Logging Standards]]
- [[backend/shared-kernel|Shared Kernel]]
- [[current-focus/DEV4-identity-verification|DEV4: Identity Verification]]
