# Employee Monitoring Override

**Area:** Configuration  
**Required Permission(s):** `monitoring:configure` + `employees:write`  
**Related Permissions:** `employees:read` (view current settings)

---

## Preconditions

- Tenant monitoring configured → [[Userflow/Workforce-Intelligence/monitoring-configuration|Monitoring Configuration]]
- Employee has GDPR consent (for enabling features) → [[Userflow/Auth-Access/gdpr-consent|Gdpr Consent]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Employee Monitoring
- **UI:** Employee Profile → Monitoring Settings tab or Settings → Monitoring → Employee Overrides → search employee
- **API:** `GET /api/v1/configuration/employee-overrides/{employeeId}`

### Step 2: Set Overrides
- **UI:** For each monitoring feature → three states:
  - **Inherit** (use tenant/department default)
  - **Force ON** (enable even if department default is OFF)
  - **Force OFF** (disable even if department default is ON)
- Set custom intervals (e.g., screenshot every 5 min instead of default 15 min)

### Step 3: Add Reason
- **UI:** Enter reason for override (required for audit trail) → e.g., "Employee in probation — enhanced monitoring" or "Privacy exemption approved by legal"
- **Backend:** EmployeeOverrideService.SetAsync() → [[modules/configuration/employee-overrides/overview|Employee Overrides]]
- **DB:** `employee_monitoring_overrides` — with reason and timestamp

### Step 4: Save
- **API:** `PUT /api/v1/configuration/employee-overrides/{employeeId}`
- **Result:** Agent picks up new policy on next heartbeat → override logged in audit trail

## Variations

### Employee consent check
- If enabling a feature the employee hasn't consented to → warning: "Employee has not given GDPR consent for this feature"

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No consent | Warning | "Consent not given — feature will not activate until consent is provided" |
| Agent not installed | Info | "Employee has no desktop agent — override saved but not active" |

## Events Triggered

- `EmployeeOverrideUpdated` → [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Workforce-Intelligence/monitoring-configuration|Monitoring Configuration]]
- [[Userflow/Configuration/monitoring-toggles|Monitoring Toggles]]
- [[Userflow/Auth-Access/gdpr-consent|Gdpr Consent]]

## Module References

- [[modules/configuration/employee-overrides/overview|Employee Overrides]]
- [[Userflow/Configuration/monitoring-toggles|Monitoring Toggles]]
- [[modules/agent-gateway/policy-distribution/overview|Policy Distribution]]
