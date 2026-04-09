# Compensation Setup

**Area:** Employee Management  
**Required Permission(s):** `employees:write` + `payroll:write`  
**Related Permissions:** `payroll:read` (view only)

---

## Preconditions

- Employee exists → [[Userflow/Employee-Management/employee-onboarding|Employee Onboarding]]
- Job family level with salary band configured → [[Userflow/Org-Structure/job-family-setup|Job Family Setup]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Navigate to Compensation
- **UI:** Employee Profile → Compensation tab → click "Edit" or "Add Salary Record"
- **API:** `GET /api/v1/employees/{id}/compensation`

### Step 2: Set Base Salary
- **UI:** Enter annual salary amount → select currency → set effective date → add reason (hire, revision, promotion)
- **Validation:** Salary checked against job family level band (warning if outside range, not blocking)

### Step 3: Configure Allowances
- **UI:** Add allowances from configured types (Housing, Transport, Meal, etc.) → set amount per allowance
- **API:** `POST /api/v1/employees/{id}/compensation`
- **Backend:** CompensationService.SetCompensationAsync() → [[modules/core-hr/compensation/overview|Compensation]]
- **DB:** `employee_compensation` — new record (previous record's `effective_to` set), `employee_allowances`

### Step 4: Enter Bank Details
- **UI:** Enter bank name, account number, routing code, SWIFT/BIC → encrypted at rest
- **DB:** `employee_bank_details` — AES-256 encrypted columns
- **Validation:** Account number format per country

### Step 5: Save
- **Result:** Salary history maintained → previous records preserved → next payroll run uses latest effective record

## Variations

### When salary revision (not initial setup)
- Previous salary record preserved with `effective_to` date
- Full salary history visible in timeline view

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Salary outside band | Warning (non-blocking) | "Salary outside band for Senior Engineer (70k-100k)" |
| Effective date in past | Validation fails | "Effective date cannot be before current salary start" |
| Invalid bank details | Validation fails | "Account number format invalid for selected country" |

## Events Triggered

- `CompensationUpdated` → [[backend/messaging/event-catalog|Event Catalog]]

## Related Flows

- [[Userflow/Employee-Management/employee-onboarding|Employee Onboarding]]
- [[Userflow/Employee-Management/employee-promotion|Employee Promotion]]
- [[Userflow/Payroll/allowance-setup|Allowance Setup]]
- [[Userflow/Payroll/payroll-run-execution|Payroll Run Execution]]

## Module References

- [[modules/core-hr/compensation/overview|Compensation]]
- [[modules/payroll/allowances/overview|Allowances]]
- [[security/data-classification|Data Classification]]
