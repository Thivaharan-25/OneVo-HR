# Monitoring Feature Toggles

**Area:** Configuration  
**Required Permission(s):** `monitoring:configure`  
**Related Permissions:** `settings:admin` (tenant-level)

---

## Preconditions

- Tenant has Workforce Intelligence pillar enabled → [[feature-flag-management]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Toggles
- **UI:** Settings → Monitoring → Feature Toggles
- **API:** `GET /api/v1/configuration/monitoring-toggles`

### Step 2: Toggle Features
- **UI:** Master grid showing each monitoring feature:
  | Feature | Tenant Default | Override Count |
  | Activity Tracking | ON | 3 employees opted out |
  | Screenshot Capture | OFF | 0 |
  | Meeting Detection | ON | 0 |
  | Idle Detection | ON | 5 custom thresholds |
  | Identity Verification | OFF | 0 |
- Toggle each ON/OFF at tenant level

### Step 3: Department Overrides
- **UI:** Click feature → see department-level overrides → enable/disable per department
- **Backend:** ConfigurationService.UpdateTogglesAsync() → [[monitoring-toggles]]
- **DB:** `monitoring_toggle_settings`

### Step 4: Save & Distribute
- **API:** `PUT /api/v1/configuration/monitoring-toggles`
- **Result:** Policy updated → agents pick up changes on next heartbeat → [[policy-distribution]]

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| No agents deployed | Info | "No agents deployed — settings will apply when agents are installed" |

## Events Triggered

- `MonitoringTogglesUpdated` → [[event-catalog]]

## Related Flows

- [[monitoring-configuration]]
- [[employee-override]]
- [[agent-deployment]]

## Module References

- [[monitoring-toggles]]
- [[configuration]]
- [[policy-distribution]]
