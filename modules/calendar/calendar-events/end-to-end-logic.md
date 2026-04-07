# Calendar Events — End-to-End Logic

**Module:** Calendar
**Feature:** Calendar Events

---

## Get Calendar Events

### Flow

```
GET /api/v1/calendar?from=2026-04-01&to=2026-04-30
  -> CalendarController.GetEvents(from, to)
    -> [Authenticated]
    -> CalendarService.GetEventsAsync(from, to, ct)
      -> 1. Get current user context (employee_id, department, teams)
      -> 2. Query calendar_events WHERE date range overlaps
         -> Filter by visibility:
            -> 'public' -> all employees see
            -> 'team' -> same team/department only
            -> 'private' -> own events only
      -> 3. Merge with leave requests (source_type = 'leave_request')
      -> 4. Merge with holidays (source_type = 'holiday')
      -> 5. Merge with review cycles (source_type = 'review_cycle')
      -> Return Result.Success(eventDtos)
```

## Create Calendar Event

### Flow

```
POST /api/v1/calendar
  -> CalendarController.Create(CreateEventCommand)
    -> [Authenticated]
    -> CalendarService.CreateAsync(command, ct)
      -> 1. Validate: title, start_date, end_date, event_type, visibility
      -> 2. INSERT into calendar_events
         -> source_type = 'manual', source_id = null
      -> Return Result.Success(eventDto)
```

### Error Scenarios

| Error | Handling |
|:------|:---------|
| End date before start date | Return 422 |
| Invalid event_type | Return 422 |
| Event not found (update/delete) | Return 404 |

## Related

- [[calendar/calendar-events/overview|Calendar Events Overview]]
- [[calendar/conflict-detection/overview|Conflict Detection]]
- [[event-catalog]]
- [[error-handling]]
