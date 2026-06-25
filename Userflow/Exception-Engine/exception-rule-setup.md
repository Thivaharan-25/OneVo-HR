# Exception Rule Setup

**Area:** Exception Engine  
**Trigger:** Admin defines anomaly detection rules (user action - configuration)
**Required Permission(s):** `exceptions:manage`  
**Related Permissions:** `monitoring:configure` (requires monitoring enabled)

---

## Preconditions

- Monitoring enabled -> [[Userflow/Monitoring/monitoring-configuration|Monitoring Configuration]]
- Data flowing from agents -> [[Userflow/Monitoring/agent-deployment|Agent Deployment]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]
- **For `non_allowed_app` rules specifically (Phase 2):** Phase 1 non-allowed app detection is owned by Activity Monitoring lightweight detection, not Exception Engine configurable rules. Phase 2 may move this into Exception Engine. See [[Userflow/Configuration/app-allowlist-setup|App Allowlist Setup]].

## Flow Steps

### Step 1: Create Rule
- **UI:** Exceptions -> Rules -> "Create Rule" -> enter name -> select category: Attendance, Productivity, Verification, Custom
- **API:** `POST /api/v1/exceptions/rules`

### Step 2: Define Condition
- **UI:** Build condition:
  - **Attendance:** "Late arrival > 15 min for 3+ days in a week" / "Absent without Time Off" / "Early departure"
  - **Activity/Productivity:** "Work-classified app time < 4h/day for 3+ days" / "Personal or non-allowed app > 2h/day" / "Idle time > 3h/day" / "Composite productivity score below threshold when score basis is comparable"
  - **App Allowlist (Phase 2):** "Non-allowed app used for more than X minutes" (`non_allowed_app` rule type). Phase 1 uses Activity Monitoring lightweight detection instead. See [[modules/activity-monitoring/overview|Activity Monitoring]].
  - **Verification (Phase 2):** "Identity verification failed". Phase 1 uses Identity Verification lightweight alerts instead. See [[modules/identity-verification/overview|Identity Verification]].
  - **Custom:** Combine multiple conditions with AND/OR
- **Backend:** ExceptionRuleService.CreateAsync() -> [[modules/exception-engine/exception-rules/overview|Exception Rules]]
- **DB:** `exception_rules` - condition stored as JSON

### Step 3: Set Severity
- **UI:** Select: Low, Medium, High, Critical -> determines notification urgency and escalation speed

### Step 4: Set Routing And Escalation
- Links: [[Userflow/Exception-Engine/escalation-chain-setup|Escalation Chain Setup]] and [[Userflow/Automation/automation-center|Automation Center (Phase 2)]]

### Step 5: Activate
- **API:** `PUT /api/v1/exceptions/rules/{id}/activate`
- **Result:** Evaluation engine checks this rule against incoming data -> [[modules/exception-engine/evaluation-engine/overview|Evaluation Engine]]

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Invalid condition | Validation fails | "Condition syntax error - check threshold values" |
| Duplicate rule name | Warning | "A rule with this name already exists" |

## Events Triggered

- `ExceptionRuleCreated` -> [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Exception-Engine/alert-review|Alert Review]]
- [[Userflow/Exception-Engine/escalation-chain-setup|Escalation Chain Setup]]
- [[Userflow/Exception-Engine/exception-dashboard|Alerts Overview]]
- [[Userflow/Monitoring/monitoring-configuration|Monitoring Configuration]]
- [[Userflow/Configuration/app-allowlist-setup|App Allowlist Setup]] - prerequisite for non_allowed_app rules

## Module References

- [[modules/exception-engine/exception-rules/overview|Exception Rules]]
- [[modules/exception-engine/evaluation-engine/overview|Evaluation Engine]]
- [[modules/exception-engine/overview|Exception Engine]]
