# Exception Rule Setup

**Area:** Exception Engine  
**Required Permission(s):** `exceptions:manage`  
**Related Permissions:** `monitoring:configure` (requires monitoring enabled)

---

## Preconditions

- Monitoring enabled → [[monitoring-configuration]]
- Data flowing from agents → [[agent-deployment]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Create Rule
- **UI:** Exceptions → Rules → "Create Rule" → enter name → select category: Attendance, Productivity, Verification, Custom
- **API:** `POST /api/v1/exceptions/rules`

### Step 2: Define Condition
- **UI:** Build condition:
  - **Attendance:** "Late arrival > 15 min for 3+ days in a week" / "Absent without leave" / "Early departure"
  - **Productivity:** "Productive hours < 4h/day for 3+ days" / "Unproductive app > 2h/day" / "Idle time > 3h/day"
  - **Verification:** "Identity verification failed" / "Agent offline > 2 hours during shift"
  - **Custom:** Combine multiple conditions with AND/OR
- **Backend:** ExceptionRuleService.CreateAsync() → [[exception-rules]]
- **DB:** `exception_rules` — condition stored as JSON

### Step 3: Set Severity
- **UI:** Select: Low, Medium, High, Critical → determines notification urgency and escalation speed

### Step 4: Set Notification Targets
- **UI:** Who gets notified: Direct Manager, HR Admin, Department Head, CEO → varies by severity
- Links: [[escalation-chain-setup]]

### Step 5: Activate
- **API:** `PUT /api/v1/exceptions/rules/{id}/activate`
- **Result:** Evaluation engine checks this rule against incoming data → [[evaluation-engine]]

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Invalid condition | Validation fails | "Condition syntax error — check threshold values" |
| Duplicate rule name | Warning | "A rule with this name already exists" |

## Events Triggered

- `ExceptionRuleCreated` → [[event-catalog]]

## Related Flows

- [[alert-review]]
- [[escalation-chain-setup]]
- [[exception-dashboard]]
- [[monitoring-configuration]]

## Module References

- [[exception-rules]]
- [[evaluation-engine]]
- [[exception-engine]]
