# Employee Monitoring Override

**Area:** Configuration  
**Trigger:** Admin overrides settings for specific employee (user action)
**Required Permission(s):** `monitoring:configure` + `employees:write`  
**Related Permissions:** `employees:read` (view current settings)

---

## Preconditions

- Tenant monitoring configured -> [[Userflow/Monitoring/monitoring-configuration|Monitoring Configuration]]
- Employee has completed required Legal & Privacy notice/consent for affected collection -> [[Userflow/Auth-Access/gdpr-consent|Legal & Privacy Acceptance]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Employee Monitoring
- **UI:** Employee Profile -> Policy & Access Overrides or Monitoring -> Employee Overrides -> search employee
- **API:** `GET /api/v1/configuration/employee-overrides/{employeeId}`

### Step 2: Set Overrides
- **UI:** For each monitoring feature -> three states:
  - **Inherit** (use tenant/department default)
  - **Force ON** (enable even if department default is OFF)
  - **Force OFF** (disable even if department default is ON)
- Set monitoring capture overrides such as screenshot capture on/off and auto screenshot on deviation on/off. Do not configure screenshot intervals.

### Step 3: Add Reason
- **UI:** Enter reason for override (required for audit trail) -> e.g., "Employee in probation - enhanced monitoring" or "Privacy exemption approved by legal"
- **Backend:** EmployeeOverrideService.SetAsync() -> [[modules/configuration/employee-overrides/overview|Employee Overrides]]
- **DB:** `employee_monitoring_overrides` - with reason and timestamp

### Step 4: Save
- **API:** `PUT /api/v1/configuration/employee-overrides/{employeeId}`
- **Result:** Agent picks up new policy on next heartbeat -> override logged in audit trail

## Variations

### Employee consent check
- If enabling a feature whose notice/consent is missing -> warning: "Employee has not completed the required Legal & Privacy item for this feature"

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Missing notice/consent | Warning | "Required Legal & Privacy item is incomplete - feature will not activate until completed" |
| Agent not installed | Info | "Employee has no desktop agent - override saved but not active" |

## Events Triggered

- `EmployeeOverrideUpdated` -> [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Monitoring/monitoring-configuration|Monitoring Configuration]]
- [[Userflow/Configuration/monitoring-toggles|Monitoring Toggles]]
- [[Userflow/Auth-Access/gdpr-consent|Legal & Privacy Acceptance]]

## Module References

- [[modules/configuration/employee-overrides/overview|Employee Overrides]]
- [[Userflow/Configuration/monitoring-toggles|Monitoring Toggles]]
- [[modules/agent-gateway/policy-distribution/overview|Policy Distribution]]
