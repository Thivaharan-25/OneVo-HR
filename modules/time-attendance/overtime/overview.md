# Overtime

**Module:** Time & Attendance
**Feature:** Overtime

---

## Purpose

Operational overtime request, detection, approval, and payroll handoff under Time & Attendance. Overtime can be requested by the employee or submitted by an authorized manager for a team member. Overtime can also be auto-flagged when attendance exceeds the configured threshold, but approval behavior is controlled by Overtime Rules.

## Product Boundary

- Overtime belongs to **Time & Attendance**.
- Calendar may show overtime-related events or reminders, but it is not the overtime management surface.
- Overtime is not a payroll-only setup screen; approved overtime feeds payroll after operational approval.
- Phase 1 overtime approvals go to Inbox and use the one eligible owner resolved through Org Structure management coverage. Do not require the Phase 2 workflow/automation engine.

## Overtime Rules Screen

**Route:** `/time-attendance/overtime-rules`

Fields:

- Applies to: `Full company`, `Departments`, `Positions`, `Employees`
- Overtime requires approval: `Yes` / `No`
- Overtime approver: `Management coverage owner`
- Minimum overtime duration: number of minutes
- Overtime starts after: `Scheduled end time` or `Total scheduled hours exceeded`
- Allow employee request: `Yes` / `No`
- Allow manager submit for team member: `Yes` / `No`

## Database Tables

### `overtime_records`
Overtime request + module-owned approval process. Workflow/Automation Engine is Phase 2 and is not required for Phase 1 overtime approval.

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `OvertimeRequested` | Employee requests or system auto-flags overtime | [[modules/notifications/overview|Notifications]] |
| `OvertimeApproved` | Authorized approver approves overtime | Payroll and audit consumers |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| POST | `/api/v1/time-attendance/overtime` | `attendance:write` | Submit overtime |
| PUT | `/api/v1/time-attendance/overtime/{id}/approve` | `attendance:approve` | Approve |

## Related

- [[modules/time-attendance/overview|Time & Attendance Module]]
- [[modules/time-attendance/presence-sessions/overview|Presence Sessions]]
- [[modules/time-attendance/shifts-schedules/overview|Shifts Schedules]]
- [[modules/time-attendance/attendance-corrections/overview|Attendance Corrections]]
- [[modules/time-attendance/device-sessions/overview|Device Sessions]]
- [[Userflow/Time-Attendance/break-tracking|Break Tracking]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[security/compliance|Compliance]]
- [[backend/shared-kernel|Shared Kernel]]
- [[current-focus/DEV4-identity-verification|DEV4: Identity Verification]]
