# Overtime

**Module:** Workforce Presence  
**Feature:** Overtime

---

## Purpose

Overtime request and approval workflow. Auto-flagged when total_present_minutes > scheduled_minutes.

## Database Tables

### `overtime_requests`
Overtime request + approval workflow.

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `OvertimeRequested` | Employee requests | [[notifications]] |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| POST | `/api/v1/workforce/overtime` | `attendance:write` | Submit overtime |
| PUT | `/api/v1/workforce/overtime/{id}/approve` | `attendance:approve` | Approve |

## Related

- [[workforce-presence|Workforce Presence Module]]
- [[presence-sessions]]
- [[shifts-schedules]]
- [[attendance-corrections]]
- [[device-sessions]]
- [[break-tracking]]
- [[multi-tenancy]]
- [[auth-architecture]]
- [[event-catalog]]
- [[compliance]]
- [[shared-kernel]]
- [[WEEK2-workforce-presence-biometric]]
