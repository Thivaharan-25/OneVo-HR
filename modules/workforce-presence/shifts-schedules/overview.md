# Shifts & Schedules

**Module:** Workforce Presence  
**Feature:** Shifts & Schedules

---

## Purpose

Shift definitions, weekly schedule patterns, templates, and employee-specific assignments/overrides.

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

- [[workforce-presence|Workforce Presence Module]]
- [[presence-sessions]]
- [[break-tracking]]
- [[overtime]]
- [[attendance-corrections]]
- [[device-sessions]]
- [[multi-tenancy]]
- [[auth-architecture]]
- [[error-handling]]
- [[shared-kernel]]
- [[WEEK2-workforce-presence-setup]]
