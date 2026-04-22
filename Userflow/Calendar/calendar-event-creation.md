# Calendar Event Creation

**Area:** Calendar  
**Trigger:** User creates calendar event (user action)
**Required Permission(s):** `calendar:write`  
**Related Permissions:** `employees:read` (add participants for individual audience)

---

## Preconditions

- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 0: Choose View
- **UI:** View toggle (Month / Week / Day) at top of Calendar page — default: Month
- Month view: grid of date cells, click a cell to select day
- Week / Day views: time-slot rows, click a slot to pre-fill date/time

### Step 1: Create Event
- **UI:** Click date/time slot or "Create Event" button → slide-in creation panel opens
- **API:** `POST /api/v1/calendar/events`

### Step 2: Enter Details
- **UI:** Enter:
  - `title` (required)
  - `description` (optional)
  - `type`: Meeting / Holiday / Training / Company Event / Out of Office
  - `date`, `start_time`, `end_time`
  - `recurrence`: None / Daily / Weekly / Monthly
  - `audience` (see Audience Rules below)
  - `color`: preset palette (optional — defaults to type color)

### Step 3: Add Participants *(individual audience only)*
- **UI:** Employee search picker — returns employees from two pools:
  1. **Hierarchy subordinates** — employees below the creator in the `reports_to_id` chain
  2. **Bypass-granted** — employees covered by an active `hierarchy_scope_exceptions` record for this user with `applies_to IS NULL OR applies_to = 'calendar'`
  
  Bypass-granted employees are shown with a **"Bypass"** badge in the search results so the creator knows they are outside normal hierarchy scope.
- **Backend:** `CalendarService.SearchParticipantsAsync()` calls `IHierarchyScope.GetSubordinateIdsAsync(featureContext: "calendar")` → [[modules/auth/authorization/end-to-end-logic|Authorization]]
- Skipped when audience is Tenant / Department / Team (participants resolved server-side)
- **DB:** `calendar_events`, `calendar_event_participants`

### Step 4: Save & Notify
- **Result:** Event visible on shared calendar → participants notified → conflicts stored

---

## Audience Rules

The `audience` field controls who receives the event. Available options depend on the creator's position in the `reports_to_id` hierarchy chain (`IHierarchyScope`).

| Audience Option | Who can select it |
|:----------------|:-----------------|
| **Tenant-wide** | Super Admin or top of org hierarchy (CEO-equivalent) only |
| **Department** | User is department head or above for that department |
| **Team** | User manages that team or is above it in hierarchy |
| **Individual** | Any user with `calendar:write` + `employees:read` scoped to that person **or covered by an active bypass grant (`applies_to = 'calendar'` or `applies_to IS NULL`)** |

- The audience picker shows only options within the creator's hierarchy scope — same `IHierarchyScope` filter used across all ONEVO modules.
- Super Admin bypasses all scoping and can target any audience.
- For Department / Team audiences, a sub-selector appears to choose the specific entity.

---

## Variations

### Company holiday
- Type = Holiday → applies to all employees in legal entity → affects leave calculations and shift schedules

### Drag-and-drop rescheduling
- User drags an existing event card to a new date/time cell → triggers `PUT /api/v1/calendar/events/{id}` with updated `start_date`/`end_date`
- Conflict check re-runs on drop — same warning as event creation
- Only events where the user has `calendar:write` can be dragged

### External sync
- Tenant admin connects Google Calendar or Outlook via tenant settings (`calendar:sync` permission)
- Synced events appear read-only with a sync badge — `source_type = 'external_sync'`
- No drag, no edit, no delete on synced events

---

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| End before start | Validation fails | "End time must be after start time" |
| Participant has conflict | Warning (non-blocking) | "[Employee] has a conflicting event at this time" |
| Selected department outside hierarchy | Blocked | "You can only create events for departments you manage" |
| Tenant-wide without top-hierarchy access | Blocked | "Tenant-wide events require elevated access" |
| Team outside reporting chain | Blocked | "You can only target teams within your reporting chain" |
| Participant added via API without bypass grant | `403 Forbidden` | "You do not have access to add this participant" |

## Events Triggered

- `CalendarEventCreated` → [[backend/messaging/event-catalog|Event Catalog]]
- Notification to resolved participants → [[backend/notification-system|Notification System]]

## Related Flows

- [[Userflow/Calendar/conflict-detection|Conflict Detection]]
- [[Userflow/Leave/leave-request-submission|Leave Request Submission]]

## Module References

- [[modules/calendar/calendar-events/overview|Calendar Events]]
- [[modules/calendar/overview|Calendar]]
