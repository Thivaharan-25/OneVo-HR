# Break Tracking

**Area:** Workforce Presence  
**Required Permission(s):** `attendance:read` (view breaks)  
**Related Permissions:** `attendance:write` (manual break entry)

---

## Preconditions

- Active presence session → [[presence-session-view]]
- Shift with break duration defined → [[shift-schedule-setup]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Automatic Break Tracking
- **Backend:** Desktop agent detects idle period → if matches break duration config → auto-marks as break
- Alternative: employee manually starts/ends break in agent tray app

### Step 2: View Break Details
- **UI:** Presence → session detail → break timeline showing: break start, end, duration, type (lunch, short break)
- **API:** `GET /api/v1/workforce/presence/sessions/{id}/breaks`

### Step 3: Break Policy Enforcement
- **Backend:** If total break time exceeds shift's allowed break duration → flagged → feeds into exception engine
- **DB:** Break data stored in `presence_session_breaks`

## Variations

### Manual break entry
- Employee with `attendance:write` can manually log missed breaks

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No break policy | Breaks tracked but not enforced | No warnings |
| Excessive breaks | Exception triggered | Manager sees alert → [[alert-review]] |

## Events Triggered

- `ExcessiveBreakDetected` → [[event-catalog]] (via exception engine)

## Related Flows

- [[presence-session-view]]
- [[shift-schedule-setup]]
- [[exception-rule-setup]]

## Module References

- [[break-tracking]]
- [[presence-sessions]]
- [[exception-rules]]
