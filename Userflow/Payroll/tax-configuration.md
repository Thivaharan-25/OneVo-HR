# Tax Configuration

**Area:** Payroll  
**Required Permission(s):** `payroll:write`  
**Related Permissions:** `settings:admin` (country-level config)

---

## Preconditions

- Legal entity with country set → [[legal-entity-setup]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Tax Config
- **UI:** Payroll → Tax Configuration → select country/legal entity
- **API:** `GET /api/v1/payroll/tax?legal_entity_id={id}`

### Step 2: Configure Tax Brackets
- **UI:** Define income tax brackets: range (0-50k → 10%, 50k-100k → 20%, 100k+ → 30%) → set for fiscal year
- **Validation:** Brackets must not overlap, must cover all ranges

### Step 3: Set Employer Contributions
- **UI:** Social security rate (employer %), health insurance (employer %), other statutory contributions → rates applied per employee on payroll run
- **DB:** `tax_configurations` — records per legal entity per year

### Step 4: Set Employee Deductions
- **UI:** Income tax (auto from brackets), social security (employee %), pension (from [[pension-configuration]]) → tax-free allowance threshold
- **API:** `POST /api/v1/payroll/tax`
- **Backend:** TaxService.ConfigureAsync() → [[tax-configuration]]

### Step 5: Save
- **Result:** Effective from next payroll run → system auto-calculates taxes per employee based on gross salary

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Overlapping brackets | Validation fails | "Tax brackets must not overlap" |
| Missing brackets | Warning | "No tax brackets cover income above 200k" |

## Events Triggered

- `TaxConfigurationUpdated` → [[event-catalog]]

## Related Flows

- [[payroll-run-execution]]
- [[pension-configuration]]
- [[legal-entity-setup]]

## Module References

- [[tax-configuration]]
- [[payroll]]
