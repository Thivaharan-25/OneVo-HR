# Monitoring Configuration

**Area:** Workforce Intelligence  
**Required Permission(s):** `monitoring:configure`  
**Related Permissions:** `settings:admin` (tenant-level), `employees:write` (employee overrides)

---

## Preconditions

- Tenant provisioned → [[tenant-provisioning]]
- GDPR consent policy configured → [[gdpr-consent]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

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
- **Backend:** ConfigurationService.UpdateMonitoringAsync() → [[monitoring-toggles]]
- **DB:** `tenant_monitoring_settings`

### Step 3: Set Data Retention
- **UI:** Set retention per data type: screenshots (30 days), activity data (90 days), raw data (7 days)
- Links: [[retention-policy-setup]]

### Step 4: Department Overrides
- **UI:** Override settings per department (e.g., disable screenshots for Legal department)

### Step 5: Save & Distribute
- **Result:** Settings saved → agents pick up new policy on next heartbeat → [[policy-distribution]]

## Variations

### Employee-level override
- Navigate to employee → Monitoring → override specific settings → [[employee-override]]
- Employee consent required → [[gdpr-consent]]

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No GDPR consent policy | Warning | "Configure consent policy before enabling monitoring" |
| Agent not deployed | Info | "12 employees have no desktop agent installed" |

## Events Triggered

- `MonitoringConfigUpdated` → [[event-catalog]]
- `PolicyDistributed` → [[event-catalog]]

## Related Flows

- [[gdpr-consent]]
- [[agent-deployment]]
- [[employee-override]]
- [[live-dashboard]]

## Module References

- [[monitoring-toggles]]
- [[tenant-settings]]
- [[employee-overrides]]
- [[configuration]]
- [[policy-distribution]]
