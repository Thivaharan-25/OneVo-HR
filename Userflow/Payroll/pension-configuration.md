# Pension Configuration

**Area:** Payroll  
**Required Permission(s):** `payroll:write`  
**Related Permissions:** `settings:admin` (scheme-level config)

---

## Preconditions

- Legal entity exists → [[Userflow/Org-Structure/legal-entity-setup|Legal Entity Setup]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Configure Pension Scheme
- **UI:** Payroll → Pension → select legal entity → "Configure Scheme"
- **API:** `POST /api/v1/payroll/pension`

### Step 2: Set Contribution Rates
- **UI:** Employee contribution % (e.g., 5%) → employer contribution % (e.g., 8%) → set contribution cap (max annual amount) → select calculation base (gross salary, base salary only)
- **Backend:** PensionService.ConfigureAsync() → [[modules/payroll/pensions/overview|Pensions]]
- **DB:** `pension_configurations`

### Step 3: Set Opt-Out Rules
- **UI:** Allow opt-out (yes/no) → if yes: minimum tenure before opt-out → re-enrollment period
- **Validation:** Must comply with country regulations

### Step 4: Set Vesting Period
- **UI:** Vesting schedule: immediate, 1 year cliff, graded over 3 years → determines when employer contributions belong to employee

### Step 5: Save & Assign
- **UI:** Assign to legal entity → all employees under entity auto-enrolled → effective from next payroll run
- **Result:** Pension deductions appear in payroll calculations

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Rate exceeds legal maximum | Warning | "Employee contribution exceeds legal limit for [Country]" |
| No scheme for entity | Warning at payroll run | "No pension scheme configured — pension deductions skipped" |

## Events Triggered

- `PensionConfigured` → [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Payroll/tax-configuration|Tax Configuration]]
- [[Userflow/Payroll/payroll-run-execution|Payroll Run Execution]]
- [[Userflow/Employee-Management/compensation-setup|Compensation Setup]]

## Module References

- [[modules/payroll/pensions/overview|Pensions]]
- [[modules/payroll/overview|Payroll]]
