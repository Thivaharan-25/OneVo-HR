# Shifts & Schedules

**Module:** Workforce Presence  
**Feature:** Shifts & Schedules

---

## Purpose

Shift definitions, weekly schedule patterns, templates, and employee-specific assignments/overrides.

**WMS bridge:** WMS reads shift data via the Availability bridge (`GET /api/v1/bridges/availability/{employeeId}`) to support sprint capacity planning and task assignment. The bridge exposes `shift.daily_start`, `shift.daily_end`, `shift.expected_daily_hours`, and `shift.working_days` — WMS uses these to calculate available capacity during a sprint period. ONEVO is canonical; WMS never stores shift data.

## Database Tables

### `shifts`
Shift definitions (morning, evening, night, flexible).

### `work_schedules`
Weekly schedule patterns.

### `employee_shift_assignments`
Which employee is on which shift.

### `schedule_templates`
Reusable schedule templates.

### `employee_work_schedules`
Employee-specific schedule overrides.

### `holidays`
Company and country holidays.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/shifts` | `attendance:read` | List shifts |
| POST | `/api/v1/shifts` | `attendance:write` | Create shift |
| GET | `/api/v1/schedules` | `attendance:read` | List schedules |
| POST | `/api/v1/schedules` | `attendance:write` | Create schedule |

## Related

- [[modules/workforce-presence/overview|Workforce Presence Module]]
- [[modules/workforce-presence/presence-sessions/overview|Presence Sessions]]
- [[Userflow/Workforce-Presence/break-tracking|Break Tracking]]
- [[modules/workforce-presence/overtime/overview|Overtime]]
- [[modules/workforce-presence/attendance-corrections/overview|Attendance Corrections]]
- [[modules/workforce-presence/device-sessions/overview|Device Sessions]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[backend/messaging/error-handling|Error Handling]]
- [[backend/shared-kernel|Shared Kernel]]
- [[current-focus/DEV3-workforce-presence-setup|DEV3: Workforce Presence]]
