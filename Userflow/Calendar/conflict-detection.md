# Calendar Conflict Detection

**Area:** Calendar  
**Required Permission(s):** `calendar:read`  
**Related Permissions:** `leave:read` (include leave in conflict check)

---

## Preconditions

- Calendar events or leave requests exist
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Automatic Conflict Check
- **Trigger:** When creating a calendar event → [[calendar-event-creation]] or submitting leave request → [[leave-request-submission]]
- **Backend:** ConflictDetectionService.CheckAsync() → [[conflict-detection]]

### Step 2: View Conflicts
- **UI:** Warning panel showing:
  - Overlapping meetings for participants
  - Approved leave during proposed meeting time
  - Public holidays on selected dates
  - Multiple events at same time for same participant

### Step 3: User Decision
- **UI:** Proceed anyway (warning only, not blocking) → or reschedule → conflict data stored as snapshot with the event/request
- **DB:** `conflict_snapshots` — point-in-time record

## Variations

### Re-check at approval time
- Leave approval re-checks conflicts with current calendar (conflicts may have changed since request was submitted)

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No calendar data | No conflicts shown | Proceeds without warnings |

## Events Triggered

- None (inline check, not standalone action)

## Related Flows

- [[calendar-event-creation]]
- [[leave-request-submission]]
- [[leave-approval]]

## Module References

- [[conflict-detection]]
- [[calendar-events]]
- [[leave-requests]]
