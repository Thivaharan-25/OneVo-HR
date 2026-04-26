# Exception Rule Setup

**Area:** Exception Engine  
**Trigger:** Admin defines anomaly detection rules (user action — configuration)
**Required Permission(s):** `exceptions:manage`  
**Related Permissions:** `monitoring:configure` (requires monitoring enabled)

---

## Preconditions

- Monitoring enabled → [[Userflow/Workforce-Intelligence/monitoring-configuration|Monitoring Configuration]]
- Data flowing from agents → [[Userflow/Workforce-Intelligence/agent-deployment|Agent Deployment]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]
- **For `non_allowed_app` rules specifically:** App allowlist must be configured first → [[Userflow/Configuration/app-allowlist-setup|App Allowlist Setup]]. Creating a `non_allowed_app` rule before the allowlist is built will produce no alerts (apps with `is_allowed = null` are never flagged).

## Flow Steps

### Step 1: Create Rule
- **UI:** Exceptions → Rules → "Create Rule" → enter name → select category: Attendance, Productivity, Verification, Custom
- **API:** `POST /api/v1/exceptions/rules`

### Step 2: Define Condition
- **UI:** Build condition:
  - **Attendance:** "Late arrival > 15 min for 3+ days in a week" / "Absent without leave" / "Early departure"
  - **Productivity:** "Productive hours < 4h/day for 3+ days" / "Unproductive app > 2h/day" / "Idle time > 3h/day"
  - **App Allowlist:** "Non-allowed app used for more than X minutes" (`non_allowed_app` rule type)
    - Requires `allowlist_mode = allowlist` and allowlist configured → [[Userflow/Configuration/app-allowlist-setup|App Allowlist Setup]]
    - Set `violation_threshold_minutes` in `threshold_json` to avoid alerting on accidental brief opens
    - Only fires on `is_allowed = false` — never on `is_allowed = null` (unreviewed apps)
  - **Verification:** "Identity verification failed" / "Agent offline > 2 hours during shift"
  - **Custom:** Combine multiple conditions with AND/OR
- **Backend:** ExceptionRuleService.CreateAsync() → [[modules/exception-engine/exception-rules/overview|Exception Rules]]
- **DB:** `exception_rules` — condition stored as JSON

### Step 3: Set Severity
- **UI:** Select: Low, Medium, High, Critical → determines notification urgency and escalation speed

### Step 4: Set Notification Targets
- **UI:** Who gets notified: Direct Manager, HR Admin, Department Head, CEO → varies by severity
- Links: [[Userflow/Exception-Engine/escalation-chain-setup|Escalation Chain Setup]]

### Step 5: Activate
- **API:** `PUT /api/v1/exceptions/rules/{id}/activate`
- **Result:** Evaluation engine checks this rule against incoming data → [[modules/exception-engine/evaluation-engine/overview|Evaluation Engine]]

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Invalid condition | Validation fails | "Condition syntax error — check threshold values" |
| Duplicate rule name | Warning | "A rule with this name already exists" |

## Events Triggered

- `ExceptionRuleCreated` → [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Exception-Engine/alert-review|Alert Review]]
- [[Userflow/Exception-Engine/escalation-chain-setup|Escalation Chain Setup]]
- [[Userflow/Exception-Engine/exception-dashboard|Alerts Overview]]
- [[Userflow/Workforce-Intelligence/monitoring-configuration|Monitoring Configuration]]
- [[Userflow/Configuration/app-allowlist-setup|App Allowlist Setup]] — prerequisite for non_allowed_app rules

## Module References

- [[modules/exception-engine/exception-rules/overview|Exception Rules]]
- [[modules/exception-engine/evaluation-engine/overview|Evaluation Engine]]
- [[modules/exception-engine/overview|Exception Engine]]
