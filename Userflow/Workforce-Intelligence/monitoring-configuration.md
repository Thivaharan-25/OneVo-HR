# Monitoring Configuration

**Area:** Workforce Intelligence  
**Trigger:** Admin enables or configures monitoring settings (user action — configuration)
**Required Permission(s):** `monitoring:configure`  
**Related Permissions:** `settings:admin` (tenant-level), `employees:write` (employee overrides)

---

## Preconditions

- Tenant provisioned → [[Userflow/Platform-Setup/tenant-provisioning|Tenant Provisioning]]
- GDPR consent policy configured → [[Userflow/Auth-Access/gdpr-consent|Gdpr Consent]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Tenant-Level Configuration
- **UI:** Settings → Monitoring → toggle master switch for activity monitoring ON/OFF
- **API:** `PUT /api/v1/configuration/monitoring`

### Step 2: Configure What's Tracked
- **UI:** Toggle each feature:
  - Activity tracking (app usage, window titles) → ON/OFF
  - Screenshot capture → ON/OFF → set interval (5/10/15/30 min)
  - Meeting detection → ON/OFF
  - Idle detection → ON/OFF → set idle threshold (5/10/15 min)
  - Identity verification → ON/OFF → set capture interval
- **Backend:** ConfigurationService.UpdateMonitoringAsync() → [[Userflow/Configuration/monitoring-toggles|Monitoring Toggles]]
- **DB:** `tenant_monitoring_settings`

### Step 3: Set Data Retention
- **UI:** Set retention per data type: screenshots (30 days), activity data (90 days), raw data (7 days)
- Links: [[Userflow/Configuration/retention-policy-setup|Retention Policy Setup]]

### Step 4: Department Overrides
- **UI:** Override settings per department (e.g., disable screenshots for Legal department)

### Step 5: Save & Distribute
- **Result:** Settings saved → agents pick up new policy on next heartbeat → [[modules/agent-gateway/policy-distribution/overview|Policy Distribution]]

## Variations

### Employee-level override
- Navigate to employee → Monitoring → override specific settings → [[Userflow/Configuration/employee-override|Employee Override]]
- Employee consent required → [[Userflow/Auth-Access/gdpr-consent|Gdpr Consent]]

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No GDPR consent policy | Warning | "Configure consent policy before enabling monitoring" |
| Agent not deployed | Info | "12 employees have no desktop agent installed" |

## Events Triggered

- `MonitoringConfigUpdated` → [[backend/messaging/event-catalog|Event Catalog]]
- `PolicyDistributed` → [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Auth-Access/gdpr-consent|Gdpr Consent]]
- [[Userflow/Workforce-Intelligence/agent-deployment|Agent Deployment]]
- [[Userflow/Configuration/employee-override|Employee Override]]
- [[Userflow/Workforce-Intelligence/live-dashboard|Live Dashboard]]

## Module References

- [[Userflow/Configuration/monitoring-toggles|Monitoring Toggles]]
- [[Userflow/Configuration/tenant-settings|Tenant Settings]]
- [[modules/configuration/employee-overrides/overview|Employee Overrides]]
- [[modules/configuration/overview|Configuration]]
- [[modules/agent-gateway/policy-distribution/overview|Policy Distribution]]
