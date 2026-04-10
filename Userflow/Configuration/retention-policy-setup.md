# Data Retention Policy Setup

**Area:** Configuration  
**Trigger:** Admin configures data retention rules (user action — configuration)
**Required Permission(s):** `settings:admin`  
**Related Permissions:** `monitoring:configure` (monitoring data retention)

---

## Preconditions

- Tenant provisioned → [[Userflow/Platform-Setup/tenant-provisioning|Tenant Provisioning]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Retention Settings
- **UI:** Settings → Data Retention
- **API:** `GET /api/v1/configuration/retention`

### Step 2: Set Retention Periods
- **UI:** Configure per data type:
  | Data Type | Default | Range |
  | Activity snapshots | 90 days | 30-365 days |
  | Screenshots | 30 days | 7-90 days |
  | Raw presence data | 365 days | 90-730 days |
  | Payroll records | 7 years | 5-10 years |
  | Audit logs | 3 years | 1-7 years |
  | Employee data (after exit) | 2 years | 1-7 years |
  | Aggregated analytics | Indefinite | 1 year-indefinite |
- **Backend:** RetentionPolicyService.UpdateAsync() → [[modules/configuration/retention-policies/overview|Retention Policies]]
- **DB:** `retention_policies`

### Step 3: Set Auto-Purge Schedule
- **UI:** Set purge frequency: Daily (off-peak), Weekly → select time window
- **Backend:** Hangfire recurring job configured → purges data past retention period

### Step 4: Save
- **API:** `PUT /api/v1/configuration/retention`
- **Result:** System automatically purges expired data per schedule → audit trail of purges maintained

## Variations

### Compliance mode
- Some data types have legal minimum retention (payroll, tax records) → system prevents setting below legal minimum

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Below legal minimum | Blocked | "Payroll records must be retained for at least 5 years" |
| Purge schedule conflict | Warning | "Purge window overlaps with payroll processing window" |

## Events Triggered

- `RetentionPolicyUpdated` → [[backend/messaging/event-catalog|Event Catalog]]
- `DataPurgeCompleted` → [[backend/messaging/event-catalog|Event Catalog]] (automated)

## Related Flows

- [[Userflow/Configuration/tenant-settings|Tenant Settings]]
- [[Userflow/Workforce-Intelligence/monitoring-configuration|Monitoring Configuration]]
- [[Userflow/Auth-Access/gdpr-consent|Gdpr Consent]]

## Module References

- [[modules/configuration/retention-policies/overview|Retention Policies]]
- [[modules/configuration/overview|Configuration]]
- [[security/data-classification|Data Classification]]
- [[security/compliance|Compliance]]
