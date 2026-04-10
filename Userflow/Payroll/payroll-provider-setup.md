# Payroll Provider Setup

**Area:** Payroll  
**Trigger:** Admin configures external payroll provider (user action — configuration)
**Required Permission(s):** `payroll:write` + `settings:admin`  
**Related Permissions:** `payroll:manage` (full provider lifecycle)

---

## Preconditions

- Legal entity exists → [[Userflow/Org-Structure/legal-entity-setup|Legal Entity Setup]]
- External provider API credentials available (if using external)
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Add Provider
- **UI:** Sidebar → Payroll → Providers → "Add Provider" → select type: Internal (ONEVO calculates) or External API (third-party payroll service)
- **API:** `POST /api/v1/payroll/providers`

### Step 2: Configure Provider
- **UI:** Enter: provider name, API endpoint (if external), API key, pay frequency (monthly/bi-weekly/weekly) → configure field mapping between ONEVO and provider format
- **Backend:** PayrollProviderService.CreateAsync() → [[modules/payroll/payroll-providers/overview|Payroll Providers]]
- **DB:** `payroll_providers` — credentials encrypted

### Step 3: Assign to Legal Entity
- **UI:** Select which legal entity uses this provider → one provider per entity
- **Validation:** Entity doesn't already have an active provider

### Step 4: Test Connection
- **UI:** Click "Test Connection" → system sends test request → shows success/failure
- **API:** `POST /api/v1/payroll/providers/{id}/test`

### Step 5: Activate
- **UI:** Toggle to Active → provider ready for payroll runs

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Connection test fails | Cannot activate | "Cannot connect to provider — check credentials" |
| Entity already has provider | Blocked | "Legal entity already assigned to [Provider Name]" |

## Events Triggered

- `PayrollProviderCreated` → [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Org-Structure/legal-entity-setup|Legal Entity Setup]]
- [[Userflow/Payroll/payroll-run-execution|Payroll Run Execution]]
- [[Userflow/Payroll/tax-configuration|Tax Configuration]]

## Module References

- [[modules/payroll/payroll-providers/overview|Payroll Providers]]
- [[backend/external-integrations|External Integrations]]
