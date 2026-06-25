# Conflict Detection

**Module:** Calendar
**Feature:** Conflict Detection

---

## Purpose

Detects overlapping calendar items for event invitations, reschedules, time off requests, and schedule-aware calendar views. Conflicts are warnings only. They do not block authorized event creation, invitation, acceptance, Time Off submission, or approval.

## Core Rule

Authority is enforcement; conflicts are warnings.

- Unauthorized assignment or invitation is blocked by permission/scope checks.
- Authorized assignment or invitation can proceed even when conflicts exist.
- Existing conflicting events are not automatically revoked, deleted, or replaced.

## Public Interface

```csharp
public interface ICalendarConflictService
{
    Task<Result<CalendarConflictSummaryDto>> GetConflictsForDateRangeAsync(
        Guid employeeId,
        DateTimeOffset startAt,
        DateTimeOffset endAt,
        CancellationToken ct);
}
```

## Conflict Summary Contract

Conflict UI should receive enough detail to show:

- Conflict count.
- Overlap range.
- Conflicting event names.
- Optional organizer/owner.

Example item:

```json
{
  "eventTitle": "Payroll review",
  "overlapStart": "2026-04-10T09:00:00+05:30",
  "overlapEnd": "2026-04-10T09:30:00+05:30",
  "ownerName": "Finance Manager"
}
```

## Recipient Actions

| Action | Placement | Behavior |
|:-------|:----------|:---------|
| Accept anyway | Inline primary | Accepts despite conflict and records conflict warning acknowledged. |
| Reject | Inline primary | Requires reason and sends it to organizer/assigner. |
| Request conflict resolution | More | Keeps response pending and sends message/explanation to organizer. |
| Nominate replacement | More | Visible only when eligible nominees exist; nominee picker is scoped by calendar rules and delegation configuration. |

Do not expose **Escalate to reporting manager** as a conflict action.

## Key Business Rules

1. Conflict checks use overlap ranges, not only dates.
2. Time off and holiday exclusions depend on the caller. Time Off workflows may exclude holidays because time off request hour calculation already handles them.
3. Conflict snapshots can be stored on the request/event at submission/send time.
4. Recipients see conflicts before responding.
5. Assigners see conflicts before sending.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/calendar/conflicts` | Authenticated with relevant calendar/time_off permission | Get conflicts for employee + date-time range |

See also: [[modules/time-off/time-off-requests/overview|Time Off Requests]], [[Userflow/Calendar/conflict-detection|Calendar Conflict Detection]]

## Related

- [[modules/calendar/overview|Calendar Module]]
- [[modules/calendar/calendar-events/overview|Calendar Events]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[backend/messaging/error-handling|Error Handling]]
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Supporting Bridges]]
