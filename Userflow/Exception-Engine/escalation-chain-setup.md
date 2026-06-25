# Escalation Chain Setup

**Area:** Alerts  
**Trigger:** Customer configures escalation paths  
**Required Permission(s):** `exceptions:manage`  
**Related Permissions:** `workflows:manage`, `employees:read`, `org:read`

---

## Preconditions

- Exception rules exist: [[Userflow/Exception-Engine/exception-rule-setup|Exception Rule Setup]]
- Required permissions are assigned through the dynamic permission model: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

---

## Flow Steps

### Step 1: Create Chain

- **UI:** Alerts -> Escalation -> Create Chain -> enter name -> select severity levels or alert types.
- **API:** `POST /api/v1/exceptions/escalation-chains`

### Step 2: Define Resolver-Based Levels

- **UI:** Add escalation levels using resolver choices:
  - Level 1: Employee's reporting manager -> notify immediately -> wait X hours for acknowledgement
  - Level 2: Users with permission `exceptions:manage` -> if unacknowledged after X hours
  - Level 3: Configured escalation resolver -> if still unacknowledged after Y hours
- **Backend:** `EscalationService.CreateChainAsync()` stores resolver type/config, delay, and action.
- **DB:** `escalation_chains`, `escalation_levels` after the approved resolver schema migration

### Step 3: Assign to Rules or Automation

- **UI:** Select which Phase 2 exception rules or Automation Center workflows use this chain. Phase 1 uses lightweight alert routing, not configurable chains.
- **Result:** When an alert is unresolved, the system resolves the next target dynamically and routes the action card through Chat or Inbox.

---

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No levels defined | Validation fails | "Add at least one escalation level" |
| Resolver returns no users | Chain pauses and notifies automation owner | "No eligible escalation recipient found" |
| Same person resolves at multiple levels | Warning | "This resolver may route multiple levels to the same person" |

## Events Triggered

- `EscalationChainCreated`
- `AlertAutoEscalated`
- `WorkflowEscalated`

## Related Flows

- [[Userflow/Automation/automation-center|Automation Center (Phase 2)]]
- [[Userflow/Exception-Engine/exception-rule-setup|Exception Rule Setup]]
- [[Userflow/Exception-Engine/alert-review|Alert Review]]

## Module References

- [[modules/exception-engine/escalation-chains/overview|Escalation Chains]]
- [[modules/exception-engine/exception-rules/overview|Exception Rules]]
- [[modules/shared-platform/workflow-engine/overview|Workflow Engine (Phase 2)]]
- [[backend/notification-system|Notification System]]
