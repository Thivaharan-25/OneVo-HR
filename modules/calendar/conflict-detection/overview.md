# Conflict Detection

**Module:** Calendar
**Feature:** Conflict Detection

---

## Purpose

Detects calendar conflicts for leave requests. Queries overlapping events for employee + date range. Excludes `leave` and `holiday` event types. Conflicts are **warnings only** — they do not block submission or approval.

## Public Interface

```csharp
public interface ICalendarConflictService
{
    Task<Result<LeaveConflictSummaryDto>> GetConflictsForDateRangeAsync(
        Guid employeeId, DateOnly startDate, DateOnly endDate, CancellationToken ct);
}
```

## Key Business Rules

1. Excludes `leave` and `holiday` event types (holidays already factored into leave day calculation).
2. Severity: `review` and `company` events are **high**, `team` and `personal` are **medium**.
3. Conflict snapshot stored as `conflict_snapshot_json` on leave request.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/calendar/conflicts` | `leave:create` or `leave:approve` | Get conflicts for employee + date range |

See also: [[leave/leave-requests]], [[2026-04-06-leave-calendar-conflict-detection]]

## Related

- [[calendar|Calendar Module]]
- [[calendar/calendar-events/overview|Calendar Events]]
- [[event-catalog]]
- [[multi-tenancy]]
- [[error-handling]]
- [[WEEK4-supporting-bridges]]
