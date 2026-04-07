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

- [[workforce-presence|Workforce Presence Module]]
- [[presence-sessions]]
- [[break-tracking]]
- [[attendance-corrections]]
- [[overtime]]
- [[shifts-schedules]]
- [[multi-tenancy]]
- [[auth-architecture]]
- [[data-classification]]
- [[shared-kernel]]
- [[WEEK2-workforce-presence-biometric]]
