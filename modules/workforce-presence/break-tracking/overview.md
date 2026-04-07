# Break Tracking

**Module:** Workforce Presence  
**Feature:** Break Tracking

---

## Purpose

Tracks breaks with auto-detection from agent idle threshold (default 15 min).

## Database Tables

### `break_records`
Fields: `employee_id`, `break_start`, `break_end` (null if ongoing), `break_type` (`lunch`, `prayer`, `smoke`, `personal`, `other`), `auto_detected`.

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `BreakExceeded` | Break exceeds allowed duration | [[exception-engine]] |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/workforce/breaks/{employeeId}` | `attendance:read` | Break records |

## Related

- [[workforce-presence|Workforce Presence Module]]
- [[presence-sessions]]
- [[device-sessions]]
- [[shifts-schedules]]
- [[attendance-corrections]]
- [[overtime]]
- [[multi-tenancy]]
- [[auth-architecture]]
- [[error-handling]]
- [[event-catalog]]
- [[shared-kernel]]
- [[WEEK2-workforce-presence-setup]]
