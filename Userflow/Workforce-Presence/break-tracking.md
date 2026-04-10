# Break Tracking

**Area:** Workforce Presence  
**Trigger:** Employee starts or ends break via clock widget (user action)
**Required Permission(s):** `attendance:read` (view breaks)  
**Related Permissions:** `attendance:write` (manual break entry)

---

## Preconditions

- Active presence session → [[Userflow/Workforce-Presence/presence-session-view|Presence Session View]]
- Shift with break duration defined → [[Userflow/Workforce-Presence/shift-schedule-setup|Shift Schedule Setup]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

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
| Excessive breaks | Exception triggered | Manager sees alert → [[Userflow/Exception-Engine/alert-review\|Alert Review]] |

## Events Triggered

- `ExcessiveBreakDetected` → [[backend/messaging/event-catalog|Event Catalog]] (via exception engine)

## Related Flows

- [[Userflow/Workforce-Presence/presence-session-view|Presence Session View]]
- [[Userflow/Workforce-Presence/shift-schedule-setup|Shift Schedule Setup]]
- [[Userflow/Exception-Engine/exception-rule-setup|Exception Rule Setup]]

## Module References

- [[Userflow/Workforce-Presence/break-tracking|Break Tracking]]
- [[modules/workforce-presence/presence-sessions/overview|Presence Sessions]]
- [[modules/exception-engine/exception-rules/overview|Exception Rules]]
