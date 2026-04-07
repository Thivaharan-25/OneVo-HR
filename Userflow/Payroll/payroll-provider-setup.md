# Payroll Provider Setup

**Area:** Payroll  
**Required Permission(s):** `payroll:write` + `settings:admin`  
**Related Permissions:** `payroll:manage` (full provider lifecycle)

---

## Preconditions

- Legal entity exists → [[legal-entity-setup]]
- External provider API credentials available (if using external)
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Add Provider
- **UI:** Sidebar → Payroll → Providers → "Add Provider" → select type: Internal (ONEVO calculates) or External API (third-party payroll service)
- **API:** `POST /api/v1/payroll/providers`

### Step 2: Configure Provider
- **UI:** Enter: provider name, API endpoint (if external), API key, pay frequency (monthly/bi-weekly/weekly) → configure field mapping between ONEVO and provider format
- **Backend:** PayrollProviderService.CreateAsync() → [[payroll-providers]]
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

- `PayrollProviderCreated` → [[event-catalog]]

## Related Flows

- [[legal-entity-setup]]
- [[payroll-run-execution]]
- [[tax-configuration]]

## Module References

- [[payroll-providers]]
- [[external-integrations]]
