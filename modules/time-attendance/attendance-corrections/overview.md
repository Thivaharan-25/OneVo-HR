# Attendance Corrections

**Module:** Time & Attendance
**Feature:** Attendance Corrections

---

## Purpose

Employee self-service and authorized manager/admin correction of attendance data with audit trail.

## Product Boundary

- Normal employees manage their own attendance.
- Managers keep their own self-attendance view and may also see employee attendance within permitted scope.
- Corrections can be row-level actions inside attendance history/log, not only a top-level correction screen.
- Clock-in Policy controls correction reasons, approval requirements, outage fallback windows, and date-effective ranges.

## Database Tables

### `attendance_corrections`
Employee, manager, or admin correction requests targeting a presence session or attendance record. Supports pending/approved/rejected/cancelled status with full audit trail. Correction types: `clock_in`, `clock_out`, `break`, `full_day`, `other`. Work area changes are excluded - use `work_area_change_requests` instead. See [[database/schemas/time-attendance#`attendance_corrections`|attendance_corrections schema]] for full column definition.

### `attendance_records`
Daily attendance summary per employee per work day. Corrections may target an attendance record via `attendance_record_id`.

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `AttendanceCorrectionRequested` | User submits correction request | Notifications and audit trail |
| `AttendanceCorrected` | Authorized correction is applied | Audit trail |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| POST | `/api/v1/time-attendance/attendance-corrections` | `attendance:write` | Submit correction |
| PUT | `/api/v1/time-attendance/attendance-corrections/{id}/approve` | `attendance:approve` | Approve correction |

## Related

- [[modules/time-attendance/overview|Time & Attendance Module]]
- [[modules/time-attendance/presence-sessions/overview|Presence Sessions]]
- [[modules/time-attendance/device-sessions/overview|Device Sessions]]
- [[modules/time-attendance/overtime/overview|Overtime]]
- [[Userflow/Time-Attendance/break-tracking|Break Tracking]]
- [[modules/time-attendance/shifts-schedules/overview|Shifts Schedules]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[backend/messaging/error-handling|Error Handling]]
- [[code-standards/logging-standards|Logging Standards]]
- [[backend/shared-kernel|Shared Kernel]]
- [[current-focus/DEV4-identity-verification|DEV4: Identity Verification]]
