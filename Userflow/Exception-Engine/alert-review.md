# Alert Review

**Area:** Exception Engine  
**Required Permission(s):** `exceptions:view` + `exceptions:acknowledge`  
**Related Permissions:** `workforce:view` (see supporting activity data)

---

## Preconditions

- Exception rules active and triggered → [[exception-rule-setup]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Receive Alert
- **UI:** Notification (in-app badge + email based on severity) → real-time via SignalR on `exception-alerts` channel
- **API:** `GET /api/v1/exceptions/alerts?status=active`

### Step 2: View Alert Details
- **UI:** Exceptions → Active Alerts → click alert → see: employee name, rule triggered, evidence data (specific metrics that breached threshold), severity, timestamp, time remaining before escalation
- **API:** `GET /api/v1/exceptions/alerts/{id}`

### Step 3: Take Action
- **UI:** Three options:
  - **Acknowledge** — "I've reviewed this" → stops escalation timer → add notes
  - **Dismiss** — false positive or acceptable → add reason → alert closed
  - **Escalate** — manually escalate to next level → [[escalation-chain-setup]]
- **API:** `PUT /api/v1/exceptions/alerts/{id}/acknowledge`
- **Backend:** AlertService.AcknowledgeAsync() → [[alert-generation]]
- **DB:** `exception_alerts` — status updated, acknowledged_by, acknowledged_at

### Step 4: Follow-Up (optional)
- Start conversation with employee → schedule meeting → create PIP if pattern persists → [[improvement-plan]]

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Alert already acknowledged | Info | "This alert was already reviewed by [Name]" |
| Escalation happened | Info | "Alert was auto-escalated to [Department Head]" |

## Events Triggered

- `AlertAcknowledged` → [[event-catalog]]
- `AlertEscalated` (if manual) → [[event-catalog]]

## Related Flows

- [[exception-rule-setup]]
- [[escalation-chain-setup]]
- [[exception-dashboard]]
- [[improvement-plan]]

## Module References

- [[alert-generation]]
- [[exception-rules]]
- [[notification-system]]
