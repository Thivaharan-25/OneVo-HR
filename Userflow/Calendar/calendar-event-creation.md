# Calendar Event Creation

**Area:** Calendar
**Trigger:** Authorized user creates a calendar event, meeting, company event, holiday, or request (user action)
**Required Permission(s):** `calendar:write`
**Related Permissions:** `employees:read` (add participants for individual audience)

---

## Preconditions

- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Calendar Boundary

Calendar is a standalone real calendar-management screen, not a dashboard card collection. It shows:

- Company events and holidays.
- Employee schedules.
- Shift and time off calendar overlays.
- Meeting/event requests.
- Invitation accept/decline behavior.
- Reminders.
- Sharing and external sync.

Time & Attendance owns **Attendance**, **Schedules**, **Clock-in Policy**, and **Overtime Rules**. Calendar may display those items as calendar overlays, but it does not replace the Time & Attendance management screens.

The UI must use a month/week/day switch, grid or timeline, compact event chips, conflict markers, and a side panel/popover for details. Do not use KPI/dashboard cards, hero cards, heavy shadows, nested cards, or automation-builder layouts for Calendar.

## Flow Steps

### Step 0: Choose View
- **UI:** View toggle (Month / Week / Day) at top of Calendar page - default: Month
- Month view: grid of date cells, click a cell to select day
- Week / Day views: time-slot rows, click a slot to pre-fill date/time

### Step 1: Create Event
- **UI:** Click date/time slot or "Create Event" button -> compact creation panel/modal opens
- **API:** `POST /api/v1/calendar`

### Step 2: Enter Details
- **UI:** Enter:
  - `title` (required)
  - `description` (optional)
  - `type`: Meeting / Holiday / Training / Company Event / Out of Office
  - `date`, `start_time`, `end_time`
  - `recurrence`: None / Daily / Weekly / Monthly
  - `audience` (see Audience Rules below)
  - `color`: preset palette (optional - defaults to type color)

### Step 3: Add Participants
- **UI:** Employee search picker returns only employees the actor is allowed to target:
  1. Employees inside the actor's backend-resolved employee visibility predicate.
  2. The predicate is resolved from Calendar rules and Org Structure management coverage where employee-data authority is required.

- **Backend:** `CalendarService.SearchParticipantsAsync()` applies the Auth employee-visibility predicate before returning searchable employees -> [[modules/auth/authorization/end-to-end-logic|Authorization]]
- **DB:** `calendar_events`, `calendar_event_participants`

### Step 4: Check Authority and Conflicts
- Authority is enforcement; conflicts are warnings.
- If the actor lacks authority to target an employee, department, legal entity, or tenant audience, the action is blocked.
- If participants have overlapping events, the conflict warning is shown before sending. The authorized actor can still send the event.
- Conflict details should include conflict count, overlap range, conflicting event names, and optional organizer/owner.

### Step 5: Send & Notify
- **Result:** Event visible on Calendar -> recipients receive invite/request in Inbox -> conflict warning snapshot stored when applicable.
- Sending an event does not automatically revoke, delete, or replace older conflicting events. Organizer may manually adjust/remove events.

---

## Audience Rules

The `audience` field controls who receives the event. Available options depend on the creator's backend-resolved employee visibility.

| Audience Option | Who can select it |
|:----------------|:-----------------|
| **Tenant-wide** | User has tenant-wide calendar permission |
| **Company** | User has permission for the selected company context |
| **Department** | User is department owner or has department-scoped calendar permission |
| **Individual** | Any user with `calendar:write` + `employees:read` scoped to that person or covered by an active bypass grant (`applies_to = 'calendar'` or `applies_to IS NULL`) |

- The audience picker shows only options allowed by backend calendar permissions and employee visibility.
- Platform/operator bypasses are internal support behavior and are not part of tenant-user calendar creation.

---

## Recipient Conflict Response

When a recipient opens an invitation with conflicts, the inline primary actions are:

- **Accept anyway** - accepts despite conflict and records that the conflict warning was acknowledged. No escalation is created.
- **Reject** - opens a required reason input and sends the reason back to the organizer/assigner.
- **More** - contains secondary actions:
  - **Request conflict resolution** - user is not deciding yet; opens an inline panel/modal to submit a message/explanation and optionally identify the blocker.
  - **Nominate replacement** - shown only when eligible nominees exist; opens a small picker scoped by calendar rules and delegation configuration with an optional note.

Do not show disabled nominee actions with explanatory text. Omit **Nominate replacement** when no eligible nominees exist. Do not use **Escalate to reporting manager** as a conflict action.

## Variations

### Legal entity holiday
- Type = Holiday -> applies to employees in selected company/legal entity context -> affects Time Off calculations and schedule overlays.
- Country holidays are normally imported through [[Userflow/Calendar/calendar-integrations|Calendar Integrations]]. Manual holiday creation is for company-specific closures that are not provided by the country calendar.

### Drag-and-drop rescheduling
- User drags an existing event card to a new date/time cell -> triggers `PUT /api/v1/calendar/{id}` with updated `start_date`/`end_date`.
- Conflict check re-runs on drop as a warning.
- Only events where the user has `calendar:write` can be dragged.

### External sync
- User connects Google Calendar or Outlook from Calendar connections. Admins manage country holiday settings from Calendar settings.
- Synced events appear with a sync badge and `source_type = 'external_sync'`.
- Synced events are read-only unless the connection is `two_way` and the current user owns the external calendar connection.

---

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| End before start | Validation fails | "End time must be after start time" |
| Participant has conflict | Warning (non-blocking) | "[Employee] has 2 conflicts: Sales sync 09:00-09:30, Time off review 09:15-10:00" |
| Selected department outside allowed coverage | Blocked | "You can only create events for departments you are allowed to target" |
| Tenant-wide without tenant-wide calendar permission | Blocked | "Tenant-wide events require elevated access" |
| Participant added via API without bypass grant | `403 Forbidden` | "You do not have access to add this participant" |

## Events Triggered

- `CalendarEventCreated` -> [[backend/messaging/event-catalog|Event Catalog]]
- Notification to resolved participants -> [[backend/notification-system|Notification System]]

## Related Flows

- [[Userflow/Calendar/conflict-detection|Conflict Detection]]
- [[Userflow/Calendar/calendar-integrations|Calendar Integrations]]
- [[Userflow/Time-Off/time-off-request-submission|Time Off Request Submission]]

## Module References

- [[modules/calendar/calendar-events/overview|Calendar Events]]
- [[modules/calendar/overview|Calendar]]
