# Calendar Event Creation

**Area:** Calendar  
**Required Permission(s):** `calendar:write`  
**Related Permissions:** `employees:read` (add participants)

---

## Preconditions

- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Create Event
- **UI:** Sidebar → Calendar → click date/time slot or "Create Event"
- **API:** `POST /api/v1/calendar/events`

### Step 2: Enter Details
- **UI:** Enter: title, description → select type (Meeting, Holiday, Training, Company Event, Out of Office) → set date, start/end time → set recurrence (none, daily, weekly, monthly)

### Step 3: Add Participants
- **UI:** Search and add employees → check conflicts → [[conflict-detection]]
- **Backend:** CalendarService.CreateEventAsync() → [[calendar-events]]
- **DB:** `calendar_events`, `calendar_event_participants`

### Step 4: Save & Notify
- **Result:** Event visible on shared calendar → participants notified → conflicts stored

## Variations

### Company holiday
- Type = Holiday → applies to all employees in legal entity → affects leave calculations and shift schedules

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| End before start | Validation fails | "End time must be after start time" |
| Participant has conflict | Warning | "[Employee] has a conflicting event at this time" |

## Events Triggered

- `CalendarEventCreated` → [[event-catalog]]
- Notification to participants → [[notification-system]]

## Related Flows

- [[conflict-detection]]
- [[leave-request-submission]]

## Module References

- [[calendar-events]]
- [[calendar]]
