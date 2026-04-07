# Identity Verification Setup

**Area:** Workforce Intelligence  
**Required Permission(s):** `verification:configure`  
**Related Permissions:** `monitoring:configure` (part of monitoring config)

---

## Preconditions

- Monitoring enabled → [[monitoring-configuration]]
- Desktop agent deployed → [[agent-deployment]]
- Employee GDPR consent for biometric data → [[gdpr-consent]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Enable Verification
- **UI:** Settings → Monitoring → Identity Verification → toggle ON
- **API:** `PUT /api/v1/configuration/identity-verification`

### Step 2: Configure Settings
- **UI:** Set capture interval (every 15/30/60 min) → set confidence threshold for face match (e.g., 85%) → set action on failure: "Alert Only" or "Lock Session" → select enrolled photo source (employee profile photo)
- **Backend:** VerificationConfigService.UpdateAsync() → [[identity-verification]]
- **DB:** `verification_settings`

### Step 3: Assign Scope
- **UI:** Apply to: all employees, specific departments, or individual employees → employees without consent automatically excluded

### Step 4: Save
- **Result:** Agent starts capturing photos at intervals → compares against enrolled photo → failures trigger alerts

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No profile photo for employee | Skipped | "5 employees have no enrolled photo — verification skipped" |
| Consent not given | Excluded | Employee auto-excluded from verification |

## Events Triggered

- `VerificationConfigUpdated` → [[event-catalog]]

## Related Flows

- [[identity-verification-review]]
- [[monitoring-configuration]]
- [[gdpr-consent]]

## Module References

- [[identity-verification]]
- [[monitoring-toggles]]
