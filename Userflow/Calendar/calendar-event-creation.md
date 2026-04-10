# Calendar Event Creation

**Area:** Calendar  
**Trigger:** User creates calendar event (user action)
**Required Permission(s):** `calendar:write`  
**Related Permissions:** `employees:read` (add participants)

---

## Preconditions

- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Create Event
- **UI:** Sidebar → Calendar → click date/time slot or "Create Event"
- **API:** `POST /api/v1/calendar/events`

### Step 2: Enter Details
- **UI:** Enter: title, description → select type (Meeting, Holiday, Training, Company Event, Out of Office) → set date, start/end time → set recurrence (none, daily, weekly, monthly)

### Step 3: Add Participants
- **UI:** Search and add employees → check conflicts → [[Userflow/Calendar/conflict-detection|Conflict Detection]]
- **Backend:** CalendarService.CreateEventAsync() → [[modules/calendar/calendar-events/overview|Calendar Events]]
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

- `CalendarEventCreated` → [[backend/messaging/event-catalog|Event Catalog]]
- Notification to participants → [[backend/notification-system|Notification System]]

## Related Flows

- [[Userflow/Calendar/conflict-detection|Conflict Detection]]
- [[Userflow/Leave/leave-request-submission|Leave Request Submission]]

## Module References

- [[modules/calendar/calendar-events/overview|Calendar Events]]
- [[modules/calendar/overview|Calendar]]
