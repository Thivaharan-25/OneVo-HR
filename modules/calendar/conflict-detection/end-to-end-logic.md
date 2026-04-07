# Conflict Detection — End-to-End Logic

**Module:** Calendar
**Feature:** Conflict Detection (for Leave)

---

## Check Conflicts for Leave Request

### Flow

```
Called by Leave module during request submission:
  -> ICalendarConflictService.GetConflictsForDateRangeAsync(employeeId, startDate, endDate, ct)
    -> 1. Query calendar_events WHERE:
       -> (start_date <= @endDate AND end_date >= @startDate) — overlap check
       -> tenant_id = current tenant
       -> event relates to employee (personal, team, or company-wide)
       -> EXCLUDE event_type IN ('leave', 'holiday') — already handled by leave calculation
    -> 2. For each conflicting event, assign severity:
       -> 'review' or 'company' events -> HIGH severity
       -> 'team' or 'personal' events -> MEDIUM severity
    -> 3. Build LeaveConflictSummaryDto:
       -> HasConflicts = conflictingEvents.Any()
       -> Conflicts = list of { EventTitle, EventDate, Severity, EventType }
       -> HighSeverityCount, MediumSeverityCount
    -> Return Result.Success(summaryDto)
```

### Key Rules

- **Conflicts are warnings only** — they never block leave submission or approval.
- **Conflict snapshot stored** on leave_request as `conflict_snapshot_json` at submission time.
- **Manager sees live re-check** during approval for events added after submission.
- **Holidays excluded** — they're already factored into leave day calculation.

## Related

- [[calendar/conflict-detection/overview|Conflict Detection Overview]]
- [[calendar/calendar-events/overview|Calendar Events]]
- [[event-catalog]]
- [[error-handling]]
