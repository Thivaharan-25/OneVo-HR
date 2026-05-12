# Monitoring Configuration

**Area:** Workforce Intelligence  
**Trigger:** Admin enables or configures monitoring settings
**Required Permission(s):** `monitoring:configure`  
**Related Permissions:** `settings:admin` (tenant-level), `employees:write` (employee overrides)

---

## Preconditions

- Tenant provisioned -> [[Userflow/Platform-Setup/tenant-provisioning|Tenant Provisioning]]
- GDPR consent policy configured -> [[Userflow/Auth-Access/gdpr-consent|Gdpr Consent]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Tenant-Level Configuration
- **UI:** Settings -> Monitoring -> toggle master switch for activity monitoring ON/OFF
- **API:** `PUT /api/v1/configuration/monitoring`

### Step 2: Configure What's Tracked
- **UI:** Toggle each feature:
  - Activity tracking (app usage, hashed window titles) -> ON/OFF
  - Screenshot capture -> ON/OFF for manual/on-demand manager commands only (no scheduled interval in Phase 1)
  - Meeting detection -> ON/OFF
  - Idle detection -> ON/OFF -> set idle threshold (5/10/15 min)
  - Identity verification -> ON/OFF -> set capture interval
  - Work-location verification -> ON/OFF -> set grace period and alert severity
- **Backend:** ConfigurationService.UpdateMonitoringAsync() -> [[Userflow/Configuration/monitoring-toggles|Monitoring Toggles]]
- **DB:** `tenant_monitoring_settings`

### Step 3: Configure Work Locations
- **UI:** Settings -> Monitoring -> Work Locations
- **Use when:** Tenant wants office, remote, or hybrid employees verified against approved work locations during paid working time
- **Flow:** Admin creates company workplaces and employee work modes -> [[Userflow/Workforce-Intelligence/work-location-compliance|Work Location Compliance]]
- **Required minimum:** Company, work location name, work location type, and at least one verification method (Wi-Fi BSSID/router MAC, public IP range, or approved VPN range)

### Step 4: Set Data Retention
- **UI:** Set retention per data type: screenshots (30 days), activity data (90 days), raw data (7 days), work-location evidence (tenant policy)
- Links: [[Userflow/Configuration/retention-policy-setup|Retention Policy Setup]]

### Step 5: Department Overrides
- **UI:** Override settings per department (e.g., disable screenshots for Legal department)

### Step 6: Save & Distribute
- **Result:** Settings saved -> agents pick up new policy on next heartbeat -> [[modules/agent-gateway/policy-distribution/overview|Policy Distribution]]

## Variations

### Employee-level override
- Navigate to employee -> Monitoring -> override specific settings -> [[Userflow/Configuration/employee-override|Employee Override]]
- Employee consent required -> [[Userflow/Auth-Access/gdpr-consent|Gdpr Consent]]

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No GDPR consent policy | Warning | "Configure consent policy before enabling monitoring" |
| Agent not deployed | Info | "12 employees have no desktop agent installed" |
| Work-location verification enabled without workplace profile | Warning | "Add at least one approved work location before enforcing this policy" |

## Events Triggered

- `MonitoringConfigUpdated` -> [[backend/messaging/event-catalog|Event Catalog]]
- `PolicyDistributed` -> [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Auth-Access/gdpr-consent|Gdpr Consent]]
- [[Userflow/Workforce-Intelligence/agent-deployment|Agent Deployment]]
- [[Userflow/Configuration/employee-override|Employee Override]]
- [[Userflow/Workforce-Intelligence/work-location-compliance|Work Location Compliance]]
- [[Userflow/Workforce-Intelligence/live-dashboard|Live Dashboard]]

## Module References

- [[Userflow/Configuration/monitoring-toggles|Monitoring Toggles]]
- [[Userflow/Configuration/tenant-settings|Tenant Settings]]
- [[modules/configuration/employee-overrides/overview|Employee Overrides]]
- [[modules/configuration/overview|Configuration]]
- [[modules/agent-gateway/policy-distribution/overview|Policy Distribution]]
- [[modules/agent-gateway/work-location-evidence|Work Location Evidence]]
