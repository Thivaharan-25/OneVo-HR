# Allowance Setup

**Area:** Payroll  
**Trigger:** Admin defines allowance types (user action — configuration)
**Required Permission(s):** `payroll:write`  
**Related Permissions:** `employees:write` (assign to employees)

---

## Preconditions

- Payroll provider configured → [[Userflow/Payroll/payroll-provider-setup|Payroll Provider Setup]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Create Allowance Type
- **UI:** Payroll → Allowances → "Create Type" → enter: name (Housing, Transport, Meal, Phone), calculation method (fixed amount / percentage of base salary)
- **API:** `POST /api/v1/payroll/allowance-types`

### Step 2: Configure Rules
- **UI:** Set taxability (fully taxable, partially exempt, tax-free) → set eligibility (all employees, by job family level, by department) → set amount or percentage
- **Backend:** AllowanceService.CreateTypeAsync() → [[modules/payroll/allowances/overview|Allowances]]
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

- `AllowanceTypeCreated` → [[backend/messaging/event-catalog|Event Catalog]]
- `AllowanceAssigned` → [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Employee-Management/compensation-setup|Compensation Setup]]
- [[Userflow/Payroll/payroll-run-execution|Payroll Run Execution]]
- [[Userflow/Payroll/tax-configuration|Tax Configuration]]

## Module References

- [[modules/payroll/allowances/overview|Allowances]]
- [[modules/core-hr/compensation/overview|Compensation]]
