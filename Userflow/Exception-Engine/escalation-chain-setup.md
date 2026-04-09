# Escalation Chain Setup

**Area:** Exception Engine  
**Required Permission(s):** `exceptions:manage`  
**Related Permissions:** `employees:read` (select escalation targets)

---

## Preconditions

- Exception rules exist → [[Userflow/Exception-Engine/exception-rule-setup|Exception Rule Setup]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Create Chain
- **UI:** Exceptions → Escalation → "Create Chain" → enter name → select which severity levels use this chain
- **API:** `POST /api/v1/exceptions/escalation-chains`

### Step 2: Define Levels
- **UI:** Add escalation levels:
  - **Level 1:** Direct Manager → notify immediately → wait X hours for acknowledgement
  - **Level 2:** HR Admin → if unacknowledged after X hours → auto-escalate
  - **Level 3:** Department Head / CEO → if still unacknowledged after Y hours
- Set time intervals between levels (e.g., 2h, 4h, 8h)
- **Backend:** EscalationService.CreateChainAsync() → [[modules/exception-engine/escalation-chains/overview|Escalation Chains]]
- **DB:** `escalation_chains`, `escalation_levels`

### Step 3: Assign to Rules
- **UI:** Select which exception rules use this chain → save
- **Result:** When alert is unacknowledged, system auto-escalates through levels

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No levels defined | Validation fails | "Add at least one escalation level" |
| Same person at multiple levels | Warning | "Same person at Level 1 and Level 2" |

## Events Triggered

- `EscalationChainCreated` → [[backend/messaging/event-catalog|Event Catalog]]
- `AlertAutoEscalated` → [[backend/messaging/event-catalog|Event Catalog]] (when triggered)

## Related Flows

- [[Userflow/Exception-Engine/exception-rule-setup|Exception Rule Setup]]
- [[Userflow/Exception-Engine/alert-review|Alert Review]]

## Module References

- [[modules/exception-engine/escalation-chains/overview|Escalation Chains]]
- [[modules/exception-engine/exception-rules/overview|Exception Rules]]
- [[backend/notification-system|Notification System]]
