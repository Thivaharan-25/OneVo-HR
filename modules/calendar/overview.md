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
| `event_type` | `varchar(30)` | `company`, `team`, `personal`, `leave`, `holiday`, `review` |
| `source_type` | `varchar(30)` | `manual`, `leave_request`, `holiday`, `review_cycle` |
| `source_id` | `uuid` | Polymorphic reference |
| `visibility` | `varchar(20)` | `public`, `team`, `private` |
| `created_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` | |

---

## Key Business Rules

1. **Unified calendar** — aggregates leave, holidays, review cycles, and custom events into one view via `source_type` + `source_id` polymorphic references.
2. **Conflict detection** — `ICalendarConflictService` queries overlapping events for a given employee + date range. Excludes `leave` and `holiday` event types (holidays are already factored into leave day count). Severity: `review` and `company` events are **high**, `team` and `personal` are **medium**. See [[Userflow/Calendar/conflict-detection|Leave-Calendar Conflict Detection]].

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/calendar` | Authenticated | Calendar events for date range |
| GET | `/api/v1/calendar/conflicts` | `leave:create` or `leave:approve` | Get conflicts for employee + date range |
| POST | `/api/v1/calendar` | Authenticated | Create event |
| PUT | `/api/v1/calendar/{id}` | Authenticated | Update event |
| DELETE | `/api/v1/calendar/{id}` | Authenticated | Delete event |

## Features

- [[modules/calendar/calendar-events/overview|Calendar Events]] — Company, team, personal, leave, holiday, and review events
- [[Userflow/Calendar/conflict-detection|Conflict Detection]] — `ICalendarConflictService` for leave request conflict warnings

---

## Related

- [[infrastructure/multi-tenancy|Multi Tenancy]] — All events are tenant-scoped
- [[backend/messaging/event-catalog|Event Catalog]] — Events sourced polymorphically from leave, holidays, review cycles
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Supporting Bridges]] — Implementation task file

See also: [[backend/module-catalog|Module Catalog]], [[modules/leave/overview|Leave]], [[modules/workforce-presence/overview|Workforce Presence]], [[Userflow/Calendar/conflict-detection|Leave-Calendar Conflict Detection]]
