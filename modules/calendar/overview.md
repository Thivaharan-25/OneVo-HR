# Module: Calendar

**Namespace:** `ONEVO.Modules.Calendar`
**Pillar:** Shared Foundation
**Owner:** Dev 1 (Week 4)
**Tables:** 1

---

## Purpose

Company-wide and team calendar events. Aggregates leave, holidays, review cycles, and custom events into a unified calendar view.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[leave]] | `ILeaveService` | Approved leave for calendar |
| **Depends on** | [[workforce-presence]] | — | Holidays |
| **Depends on** | [[performance]] | — | Review cycle dates |
| **Consumed by** | [[leave]] | `ICalendarConflictService` | Conflict detection for leave requests |

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
2. **Conflict detection** — `ICalendarConflictService` queries overlapping events for a given employee + date range. Excludes `leave` and `holiday` event types (holidays are already factored into leave day count). Severity: `review` and `company` events are **high**, `team` and `personal` are **medium**. See [[2026-04-06-leave-calendar-conflict-detection]].

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

- [[calendar-events]] — Company, team, personal, leave, holiday, and review events
- [[conflict-detection]] — `ICalendarConflictService` for leave request conflict warnings

---

## Related

- [[multi-tenancy]] — All events are tenant-scoped
- [[event-catalog]] — Events sourced polymorphically from leave, holidays, review cycles
- [[WEEK4-supporting-bridges]] — Implementation task file

See also: [[module-catalog]], [[leave]], [[workforce-presence]], [[2026-04-06-leave-calendar-conflict-detection]]
