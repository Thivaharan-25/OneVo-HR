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

- [[workforce-presence|Workforce Presence Module]]
- [[presence-sessions]]
- [[device-sessions]]
- [[overtime]]
- [[break-tracking]]
- [[shifts-schedules]]
- [[multi-tenancy]]
- [[auth-architecture]]
- [[error-handling]]
- [[logging-standards]]
- [[shared-kernel]]
- [[WEEK2-workforce-presence-biometric]]
