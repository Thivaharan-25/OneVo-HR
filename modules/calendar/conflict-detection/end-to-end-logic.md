# Conflict Detection - End-to-End Logic

**Module:** Calendar
**Feature:** Conflict Detection

---

## Check Conflicts for Event or Time Off Request

### Flow

```
Called by Calendar event creation, invitation response, reschedule, or Time Off request submission:
  -> ICalendarConflictService.GetConflictsForDateRangeAsync(employeeId, startAt, endAt, ct)
    -> 1. Query calendar_events WHERE:
       -> (start_date < @endAt AND end_date > @startAt) -- overlap check
       -> tenant_id = current tenant
       -> employee is owner/participant or event applies to an allowed audience
       -> apply caller-specific exclusions
    -> 2. For each conflict, calculate:
       -> overlap_start = max(event.start_date, requested.startAt)
       -> overlap_end = min(event.end_date, requested.endAt)
    -> 3. Build CalendarConflictSummaryDto:
       -> HasConflicts = conflictingEvents.Any()
       -> ConflictCount
       -> Conflicts = list of { EventTitle, OverlapStart, OverlapEnd, EventType, OwnerName? }
    -> Return Result.Success(summaryDto)
```

### Event Creation Rule

```
CalendarService.CreateAsync(command)
  -> Validate actor authority for audience/participants
     -> if unauthorized, block with 403
  -> Check conflicts
     -> return warnings, never block authorized creation
  -> Save event and participants
  -> Notify recipients
```

### Invitation Response Rule

```
Recipient opens invitation
  -> Load current conflicts
  -> Show inline actions:
       Accept anyway
       Reject
       More
  -> More includes:
       Request conflict resolution
       Nominate replacement only when eligible nominees exist
```

## Key Rules

- **Authority is enforcement; conflicts are warnings.**
- **Conflicts are warnings only** - they never block authorized event creation, invitation response, Time Off submission, or Time Off approval.
- **No automatic revocation** - old conflicting events remain until an organizer manually adjusts/removes them.
- **Reject** means declining and requires a reason.
- **Request conflict resolution** means no decision yet; the organizer must resolve or clarify the conflict.
- **Nominate replacement** is hidden when no eligible nominees exist.
- **Holidays in Time Off workflows** may be excluded because they are already factored into Time Off request hour calculation.
- **Conflict snapshot stored** on the relevant request/event when the caller needs point-in-time audit.
- **Assigned owner/approver can see live re-check** during approval for events added after submission.

## Related

- [[modules/calendar/conflict-detection/overview|Conflict Detection Overview]]
- [[modules/calendar/calendar-events/overview|Calendar Events]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/messaging/error-handling|Error Handling]]
