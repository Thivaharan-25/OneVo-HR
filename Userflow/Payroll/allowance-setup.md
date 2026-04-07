# Allowance Setup

**Area:** Payroll  
**Required Permission(s):** `payroll:write`  
**Related Permissions:** `employees:write` (assign to employees)

---

## Preconditions

- Payroll provider configured → [[payroll-provider-setup]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Create Allowance Type
- **UI:** Payroll → Allowances → "Create Type" → enter: name (Housing, Transport, Meal, Phone), calculation method (fixed amount / percentage of base salary)
- **API:** `POST /api/v1/payroll/allowance-types`

### Step 2: Configure Rules
- **UI:** Set taxability (fully taxable, partially exempt, tax-free) → set eligibility (all employees, by job family level, by department) → set amount or percentage
- **Backend:** AllowanceService.CreateTypeAsync() → [[allowances]]
- **DB:** `allowance_types`

### Step 3: Assign to Employees
- **UI:** Bulk assign (by eligibility rule) or individual: Employee Profile → Compensation → Add Allowance → select type → set amount → set effective date
- **API:** `POST /api/v1/employees/{id}/allowances`
- **DB:** `employee_allowances`

### Step 4: Payroll Integration
- **Result:** Allowances auto-included in payroll run calculations → shown as separate line items in payslip

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Duplicate type name | Validation fails | "Allowance type already exists" |
| Percentage > 100% | Validation fails | "Percentage cannot exceed 100%" |

## Events Triggered

- `AllowanceTypeCreated` → [[event-catalog]]
- `AllowanceAssigned` → [[event-catalog]]

## Related Flows

- [[compensation-setup]]
- [[payroll-run-execution]]
- [[tax-configuration]]

## Module References

- [[allowances]]
- [[compensation]]
