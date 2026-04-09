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

See also: [[modules/leave/leave-requests/overview|Leave Requests]], [[Userflow/Calendar/conflict-detection|Leave-Calendar Conflict Detection]]

## Related

- [[modules/calendar/overview|Calendar Module]]
- [[frontend/architecture/overview|Calendar Events]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[backend/messaging/error-handling|Error Handling]]
- [[current-focus/DEV4-shared-platform-agent-gateway|DEV4: Supporting Bridges]]
