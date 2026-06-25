# Calendar Conflict Detection

**Area:** Calendar
**Trigger:** System checks for scheduling conflicts on event creation, invitation response, reschedule, or time off request (system-triggered - automatic)
**Required Permission(s):** `calendar:read`
**Related Permissions:** `time_off:read` (include time off in conflict check)

---

## Preconditions

- Calendar events, schedules, or time off requests exist.
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Core Rule

Authority is enforcement; conflicts are warnings.

- If the actor lacks authority to assign or invite a person/scope, the action is blocked.
- If the actor has authority but the target has conflicting calendar items, the system warns and allows the authorized action to continue.
- Conflict warnings do not automatically revoke, delete, or replace existing events.

## Flow Steps

### Step 1: Automatic Conflict Check
- **Trigger:** Creating a calendar event -> [[Userflow/Calendar/calendar-event-creation|Calendar Event Creation]], responding to an invitation, rescheduling an event, or submitting time off request -> [[Userflow/Time-Off/time-off-request-submission|Time Off Request Submission]]
- **Backend:** ConflictDetectionService.CheckAsync() -> [[modules/calendar/conflict-detection/overview|Conflict Detection]]

### Step 2: View Conflicts
- **UI warning panel shows:**
  - Conflict count.
  - Overlap range.
  - Conflicting event names.
  - Optional organizer/owner.

Example banner:

> 2 conflicts found for Amal Perera: "Payroll review" overlaps 09:00-09:30 and "Customer call" overlaps 09:15-10:00. You can still send this event if you have authority.

### Step 3: Assigner Decision
- **UI:** Assigner sees warning before sending.
- **Allowed actions:** Send anyway, edit/reschedule, remove participant, or cancel creation.
- **DB:** Conflict warning snapshot stored with the event/request when applicable.

### Step 4: Recipient Decision
- **UI inline primary actions:**
  - **Accept anyway**
  - **Reject**
  - **More**
- **More menu actions:**
  - **Request conflict resolution**
  - **Nominate replacement** only when eligible nominees exist

Reject means declining the invitation/request. Request conflict resolution means the recipient has not declined and needs the organizer to resolve the conflict first. They are not interchangeable.

## Action Details

| Action | Behavior |
|:-------|:---------|
| Accept anyway | Accepts despite conflict and records conflict warning acknowledged. No escalation. |
| Reject | Opens required reason input and submits reason to organizer/assigner. |
| Request conflict resolution | Opens inline panel/modal for message/explanation and optional blocker. Keeps decision pending. |
| Nominate replacement | Opens small picker. Valid nominees come from calendar rules and delegation configuration. Optional note. Only visible when eligible nominees exist. |

Do not bring back **Escalate to reporting manager**.

## Variations

### Re-check at approval time
- Time Off approval re-checks conflicts with current calendar because conflicts may have changed since request submission.

### Audience expansion for conflict check
- When `audience_type = tenant`, conflict warnings can be summarized instead of listing every employee.
- Conflict warnings are grouped by employee in the warning panel.

### Re-check on drag-and-drop reschedule
- When user drags an event to a new time slot, conflict check re-runs automatically against the new date/time range.

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No calendar data | No conflicts shown | Proceeds without warnings |
| Actor lacks authority | Blocked | "You do not have access to assign this event" |

## Events Triggered

- None for inline warning checks.
- Invitation response events may be emitted by Calendar Events.

## Related Flows

- [[Userflow/Calendar/calendar-event-creation|Calendar Event Creation]]
- [[Userflow/Time-Off/time-off-request-submission|Time Off Request Submission]]
- [[Userflow/Time-Off/time-off-approval|Time Off Approval]]

## Module References

- [[modules/calendar/conflict-detection/overview|Conflict Detection]]
- [[modules/calendar/calendar-events/overview|Calendar Events]]
- [[modules/time-off/time-off-requests/overview|Time Off Requests]]
