# Monitoring Feature Toggles

**Area:** Configuration  
**Trigger:** Admin toggles monitoring features on/off (user action - configuration)
**Required Permission(s):** `monitoring:configure`  
**Related Permissions:** `settings:admin` (tenant-level)

---

## Preconditions

- Tenant has Monitoring pillar enabled -> [[Userflow/Platform-Setup/feature-flag-management|Feature Flag Management]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Toggles
- **UI:** Monitoring -> Feature Toggles
- **API:** `GET /api/v1/configuration/monitoring-toggles`

### Step 2: Toggle Features
- **UI:** Master grid showing each monitoring feature:
  | Feature | Tenant Default | Override Count |
  | Activity Tracking | ON | 3 employees opted out |
  | Application Tracking | ON | 0 |
  | Screenshot Capture | OFF | 0 |
  | Meeting Detection | ON | 0 |
  | Idle Detection | ON | 5 custom thresholds |
  | Identity Verification | OFF | 0 |
  | Work Location Verification | OFF | 0 |
- Toggle each ON/OFF at tenant level

### Step 2b: Configure App Allowlist Mode
- **UI:** Below feature toggles -> App Allowlist section:
  - **Mode:** `Off` (no enforcement) / `Blocklist` (only listed-as-blocked apps flagged) / `Allowlist` (only approved apps allowed)
  - **Recommended during initial setup:** set to `Blocklist` while the allowlist is being built - prevents false alerts during the discovery period
  - **Switch to `Allowlist`** only after reviewing Discovered Apps and configuring the allowlist -> [[Userflow/Configuration/app-allowlist-setup|App Allowlist Setup]]
- **API:** `PUT /api/v1/configuration/monitoring-toggles` (includes `allowlist_mode` field)
- **DB:** `monitoring_feature_toggles`

### Step 3: Department Overrides
- **UI:** Click feature -> see department-level overrides -> enable/disable per department
- **Backend:** ConfigurationService.UpdateTogglesAsync() -> [[Userflow/Configuration/monitoring-toggles|Monitoring Toggles]]
- **DB:** `monitoring_toggle_settings`

### Step 4: Save & Distribute
- **API:** `PUT /api/v1/configuration/monitoring-toggles`
- **Result:** Policy updated -> agents pick up changes on next heartbeat -> [[modules/agent-gateway/policy-distribution/overview|Policy Distribution]]

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No agents deployed | Info | "No agents deployed - settings will apply when agents are installed" |

### Step 5: Configure Monitoring Alert Routing Policy
- **UI:** Below feature toggles -> **Alert Routing Policy** section:
  - **Recipient Resolver:** `Management Coverage Availability Chain` (default) / `Reporting Manager`
  - **Grace Window (minutes):** How long to wait for a scheduled recipient before skipping (default: 15)
  - **Fallback to Management Coverage Chain:** (visible only when Reporting Manager is selected) toggle ON/OFF (default: ON)
  - **Unresolved Routing Action:** `Create Routing Issue` (default) / `Leave Unassigned`
- **API:** `PUT /api/v1/configuration/monitoring-alert-policy`
- **DB:** `monitoring_alert_policy`
- **Tooltip:** "Controls who receives monitoring alerts. Management Coverage Availability Chain routes to the first available responsible person from the employee's active management coverage assignments. Reporting Manager routes to the position hierarchy reporting manager."

## Events Triggered

- `MonitoringTogglesUpdated` -> [[backend/messaging/event-catalog|Event Catalog]]
- `MonitoringAlertPolicyUpdated` -> [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Monitoring/monitoring-configuration|Monitoring Configuration]]
- [[Userflow/Monitoring/work-location-compliance|Work Location Compliance]]
- [[Userflow/Configuration/employee-override|Employee Override]]
- [[Userflow/Configuration/app-allowlist-setup|App Allowlist Setup]] - configure which apps are allowed/blocked
- [[Userflow/Monitoring/agent-deployment|Agent Deployment]]

## Module References

- [[Userflow/Configuration/monitoring-toggles|Monitoring Toggles]]
- [[modules/configuration/overview|Configuration]]
- [[modules/agent-gateway/policy-distribution/overview|Policy Distribution]]
