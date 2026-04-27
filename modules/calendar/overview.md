# Module: Calendar

**Namespace:** `ONEVO.Modules.Calendar`
**Phase:** 1 — Build
**Pillar:** Shared Foundation
**Owner:** Dev 3
**Tables:** 1
**Task File:** [[current-focus/DEV3-calendar|DEV3: Calendar]]

---

## Purpose

Company-wide and team calendar events. Aggregates leave, holidays, review cycles, and custom events into a unified calendar view.

The Calendar's sidebar also surfaces three workforce management features: **Shifts & Schedules** (shift creation, schedule templates, employee assignments), **Attendance Correction** (manager corrections to presence data), and **Overtime** (overtime request and approval). The backend logic for all three lives in [[modules/workforce-presence/overview|Workforce Presence]]; the UI entry points are the Calendar sidebar panel.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[modules/leave/overview\|Leave]] | `ILeaveService` | Approved leave for calendar |
| **Depends on** | [[modules/workforce-presence/overview\|Workforce Presence]] | — | Holidays |
| **Depends on** | [[database/performance\|Performance]] | — | Review cycle dates |
| **Consumed by** | [[modules/leave/overview\|Leave]] | `ICalendarConflictService` | Conflict detection for leave requests |

---

## Public Interface

```csharp
// ONEVO.Modules.Calendar/Public/ICalendarConflictService.cs
public interface ICalendarConflictService
{
    /// <summary>
    /// Returns calendar events that overlap with the given date range for an employee.
    /// Used by Leave module to show conflict warnings during submission and approval.
    /// Excludes 'leave' and 'holiday' event types (holidays are already factored into leave day calculation).
    /// </summary>
    Task<Result<LeaveConflictSummaryDto>> GetConflictsForDateRangeAsync(
        Guid employeeId, DateOnly startDate, DateOnly endDate, CancellationToken ct);
}
```

---

## Code Location (Clean Architecture)

Domain entities:
  ONEVO.Domain/Features/Calendar/Entities/
  ONEVO.Domain/Features/Calendar/Events/

Application (CQRS):
  ONEVO.Application/Features/Calendar/Commands/
  ONEVO.Application/Features/Calendar/Queries/
  ONEVO.Application/Features/Calendar/DTOs/Requests/
  ONEVO.Application/Features/Calendar/DTOs/Responses/
  ONEVO.Application/Features/Calendar/Validators/
  ONEVO.Application/Features/Calendar/EventHandlers/

Infrastructure:
  ONEVO.Infrastructure/Persistence/Configurations/Calendar/

API endpoints:
  ONEVO.Api/Controllers/Calendar/CalendarController.cs

---

## Database Tables (1)

### `calendar_events`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `title` | `varchar(200)` | |
| `description` | `text` | |
| `start_date` | `timestamptz` | |
| `end_date` | `timestamptz` | |
| `event_type` | `varchar(30)` | `meeting`, `company`, `team`, `personal`, `leave`, `holiday`, `training`, `out_of_office`, `review` |
| `source_type` | `varchar(30)` | `manual`, `leave_request`, `holiday`, `review_cycle`, `external_sync` |
| `source_id` | `uuid` | Polymorphic reference |
| `audience_type` | `varchar(20)` | `tenant`, `department`, `team`, `individual` |
| `audience_id` | `uuid` | FK → departments/teams/employees; null for tenant-wide |
| `color` | `varchar(7)` | Hex color; nullable |
| `recurrence` | `varchar(20)` | `none`, `daily`, `weekly`, `monthly` |
| `visibility` | `varchar(20)` | `public`, `team`, `private` |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` | |

---

## Key Business Rules

1. **Unified calendar** — aggregates leave, holidays, review cycles, and custom events into one view via `source_type` + `source_id` polymorphic references.
2. **Conflict detection** — `ICalendarConflictService` queries overlapping events for a given employee + date range. Excludes `leave` and `holiday` event types. Severity: `review` and `company` events are **high**, `team` and `personal` are **medium**. See [[Userflow/Calendar/conflict-detection|Leave-Calendar Conflict Detection]].
3. **Hierarchy-scoped audience** — `audience_type` determines who receives the event. Available options are filtered by `IHierarchyScope`: a user can only target entities in their reporting chain. Super Admin bypasses scoping. For `department`/`team` audiences, participants are resolved server-side before conflict checks run.
4. **External sync** — events with `source_type = external_sync` are read-only; they cannot be edited, deleted, or dragged.

---

## Domain Events (intra-module — MediatR)

> These events are published and consumed within this module only. They never leave the module.

| Event | Published When | Handler |
|:------|:---------------|:--------|
| _(none)_ | — | — |

## Integration Events (cross-module — RabbitMQ)

### Publishes

| Event | Routing Key | Published When | Consumers |
|:------|:-----------|:---------------|:----------|
| _(none)_ | — | — | — |

### Consumes

| Event | Routing Key | Source Module | Action Taken |
|:------|:-----------|:-------------|:-------------|
| `LeaveApproved` | `leave.request.approved` | [[modules/leave/overview\|Leave]] | Create a `leave` calendar event for the approved leave period |
| `ReviewCycleStarted` | `performance.review.started` | [[modules/performance/overview\|Performance]] | Create a `review` calendar event for the cycle dates |
| `EmployeeHired` | `core-hr.employee.hired` | [[modules/core-hr/overview\|Core HR]] | Seed onboarding events for new employee |

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/calendar` | Authenticated | Calendar events for date range |
| GET | `/api/v1/calendar/conflicts` | `leave:create` or `leave:approve` | Get conflicts for employee + date range |
| POST | `/api/v1/calendar` | `calendar:write` | Create event |
| PUT | `/api/v1/calendar/{id}` | `calendar:write` | Update event (reschedule via drag-and-drop uses this) |
| DELETE | `/api/v1/calendar/{id}` | `calendar:write` | Delete event |

## Features

- [[modules/calendar/calendar-events/overview|Calendar Events]] — Company, team, personal, leave, holiday, training, out-of-office, and review events
- [[Userflow/Calendar/conflict-detection|Conflict Detection]] — `ICalendarConflictService` for leave request conflict warnings

---

## Related

- [[infrastructure/multi-tenancy|Multi Tenancy]] — All events are tenant-scoped
- [[backend/messaging/event-catalog|Event Catalog]] — Events sourced polymorphically from leave, holidays, review cycles
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Supporting Bridges]] — Implementation task file

See also: [[backend/module-catalog|Module Catalog]], [[modules/leave/overview|Leave]], [[modules/workforce-presence/overview|Workforce Presence]], [[Userflow/Calendar/conflict-detection|Leave-Calendar Conflict Detection]]

## Calendar Panel Navigation Items

The Calendar pillar expansion panel contains four items:

| Label | Route | Purpose |
|---|---|---|
| Calendar | `/calendar` | Unified view — leave dates, public holidays, review cycles, and shift schedule overlays |
| Schedules | `/calendar/schedule` | Shift schedule management — view and edit employee shift patterns |
| Attendance | `/calendar/attendance` | Attendance correction requests — adjust clock-in/out records |
| Overtime | `/calendar/overtime` | Overtime request submission and approval |

**Why scheduling lives in Calendar (not Workforce):**
Schedules, Attendance, and Overtime are time-visual concepts — they are understood in the context of a calendar timeline. The Workforce pillar is for doing work (projects, tasks). The Calendar pillar is for scheduling when work happens.

**Connection to WMS:**
- Shift schedule hours from this module feed into WMS Resource Management as the available capacity baseline for each employee.
- Approved timesheets from WMS Time Tracking create Attendance correction records here when discrepancies exist.
- Excess hours from approved timesheets create Overtime entries here for manager approval.

See [[Userflow/Work-Management/time-tracking-flow|Time Tracking Flow]] for the full overtime and attendance connection.
