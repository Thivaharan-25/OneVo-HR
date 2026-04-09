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
| `OvertimeRequested` | Employee requests | [[modules/notifications/overview|Notifications]] |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| POST | `/api/v1/workforce/overtime` | `attendance:write` | Submit overtime |
| PUT | `/api/v1/workforce/overtime/{id}/approve` | `attendance:approve` | Approve |

## Related

- [[modules/workforce-presence/overview|Workforce Presence Module]]
- [[modules/workforce-presence/presence-sessions/overview|Presence Sessions]]
- [[modules/workforce-presence/shifts-schedules/overview|Shifts Schedules]]
- [[modules/workforce-presence/attendance-corrections/overview|Attendance Corrections]]
- [[modules/workforce-presence/device-sessions/overview|Device Sessions]]
- [[Userflow/Workforce-Presence/break-tracking|Break Tracking]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[security/compliance|Compliance]]
- [[backend/shared-kernel|Shared Kernel]]
- [[current-focus/DEV4-identity-verification|DEV4: Identity Verification]]
