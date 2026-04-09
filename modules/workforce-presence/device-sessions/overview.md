# Device Sessions

**Module:** Workforce Presence  
**Feature:** Device Sessions

---

## Purpose

Tracks laptop active/idle cycles. MULTIPLE rows per employee per day (one per active/idle cycle). Do NOT confuse with `presence_sessions` (one row per day).

## Database Tables

### `device_sessions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `device_id` | `uuid` | FK → registered_agents |
| `session_start` | `timestamptz` | |
| `session_end` | `timestamptz` | Null if ongoing |
| `active_minutes` | `int` | |
| `idle_minutes` | `int` | |
| `active_percentage` | `decimal(5,2)` | |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/workforce/device-sessions/{employeeId}` | `workforce:view` | Device sessions |

## Related

- [[modules/workforce-presence/overview|Workforce Presence Module]]
- [[modules/workforce-presence/presence-sessions/overview|Presence Sessions]]
- [[Userflow/Workforce-Presence/break-tracking|Break Tracking]]
- [[modules/workforce-presence/attendance-corrections/overview|Attendance Corrections]]
- [[modules/workforce-presence/overtime/overview|Overtime]]
- [[modules/workforce-presence/shifts-schedules/overview|Shifts Schedules]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[security/data-classification|Data Classification]]
- [[backend/shared-kernel|Shared Kernel]]
- [[current-focus/DEV4-identity-verification|DEV4: Identity Verification]]
