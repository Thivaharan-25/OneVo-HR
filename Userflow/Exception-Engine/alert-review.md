# Alert Review

**Area:** Exception Engine  
**Trigger:** Reviewer opens flagged alert (reaction — triggered by exception detection)
**Required Permission(s):** `exceptions:view` + `exceptions:acknowledge`  
**Related Permissions:** `workforce:view` (see supporting activity data)

---

## Preconditions

- Exception rules active and triggered → [[Userflow/Exception-Engine/exception-rule-setup|Exception Rule Setup]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

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
  - **Escalate** — manually escalate to next level → [[Userflow/Exception-Engine/escalation-chain-setup|Escalation Chain Setup]]
- **API:** `PUT /api/v1/exceptions/alerts/{id}/acknowledge`
- **Backend:** AlertService.AcknowledgeAsync() → [[modules/exception-engine/alert-generation/overview|Alert Generation]]
- **DB:** `exception_alerts` — status updated, acknowledged_by, acknowledged_at

### Step 4: Follow-Up (optional)
- Start conversation with employee → schedule meeting → create PIP if pattern persists → [[Userflow/Performance/improvement-plan|Improvement Plan]]

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Alert already acknowledged | Info | "This alert was already reviewed by [Name]" |
| Escalation happened | Info | "Alert was auto-escalated to [Department Head]" |

## Events Triggered

- `AlertAcknowledged` → [[backend/messaging/event-catalog|Event Catalog]]
- `AlertEscalated` (if manual) → [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Exception-Engine/exception-rule-setup|Exception Rule Setup]]
- [[Userflow/Exception-Engine/escalation-chain-setup|Escalation Chain Setup]]
- [[Userflow/Exception-Engine/exception-dashboard|Alerts Overview]]
- [[Userflow/Performance/improvement-plan|Improvement Plan]]

## Module References

- [[modules/exception-engine/alert-generation/overview|Alert Generation]]
- [[modules/exception-engine/exception-rules/overview|Exception Rules]]
- [[backend/notification-system|Notification System]]
