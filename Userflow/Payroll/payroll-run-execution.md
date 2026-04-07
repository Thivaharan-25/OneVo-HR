# Payroll Run Execution

**Area:** Payroll  
**Required Permission(s):** `payroll:run` (execute) + `payroll:approve` (final approval)  
**Related Permissions:** `payroll:read` (view results), `employees:read` (verify employee data)

---

## Preconditions

- Payroll provider configured → [[payroll-provider-setup]]
- Tax rules set → [[tax-configuration]]
- Employee compensation records exist → [[compensation-setup]]
- Leave and attendance data up to date → [[leave-approval]], [[presence-session-view]]
- Required permissions: [[permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Create Payroll Run
- **UI:** Payroll → Runs → "Create Run" → select pay period (e.g., March 2026) → select legal entity → click "Calculate"
- **API:** `POST /api/v1/payroll/runs`
- **Backend:** PayrollRunService.InitiateAsync() → [[payroll-execution]]

### Step 2: System Calculates (Automated via Hangfire)
- **Backend:** For each employee in legal entity:
  1. **Gross Salary** = base salary (prorated if mid-month join/leave)
  2. **+ Allowances** = housing + transport + meal + other → [[allowances]]
  3. **+ Overtime** = approved overtime hours × overtime rate → [[overtime-management]]
  4. **+ Expense Reimbursements** = approved expense claims → [[expense-approval]]
  5. **- Unpaid Leave** = unpaid leave days × daily rate → [[leave-approval]]
  6. **- Tax** = income tax from brackets → [[tax-configuration]]
  7. **- Pension (employee)** = contribution % → [[pension-configuration]]
  8. **- Other deductions** = loans, advances, disciplinary
  9. **= Net Pay**
  10. **Employer costs** = employer pension + employer social security
- **DB:** `payroll_runs`, `payroll_line_items` — per employee breakdown

### Step 3: Review Summary
- **UI:** Payroll run summary dashboard: total gross, total deductions, total net, employee count → flag any anomalies (salary changes, new hires, terminations this period) → drill down per employee to see line-item detail
- **API:** `GET /api/v1/payroll/runs/{id}`

### Step 4: Submit for Approval
- **UI:** Click "Submit for Approval" → run locked for editing → approver notified
- **API:** `POST /api/v1/payroll/runs/{id}/submit`
- **DB:** `payroll_runs.status` → "Pending Approval"

### Step 5: Approve
- **UI:** Approver (with `payroll:approve`) reviews → clicks "Approve" → run finalized
- **API:** `POST /api/v1/payroll/runs/{id}/approve`
- **DB:** Status → "Approved"

### Step 6: Post-Approval Processing
- **Backend:**
  1. Payslips generated (PDF) per employee → [[document-management]]
  2. Employees notified → [[notification-system]]
  3. Provider sync triggered (if external provider) → [[payroll-provider-setup]]
  4. Accounting entries created
  5. Bank file generated for payment processing

## Variations

### When run has errors
- Red flags on problematic employees (missing bank details, no tax config) → must resolve before approval

### Supplementary run
- For corrections or off-cycle payments → creates additional run for same period

## Error Scenarios

| Scenario | What happens | User sees |
|:---------|:-------------|:----------|
| Missing bank details | Employee flagged | "3 employees missing bank details" |
| No tax config for country | Blocked | "Tax configuration required for [Country]" |
| Duplicate run for period | Warning | "A run already exists for March 2026" |
| Approval rejected | Run reopened | "Run rejected — review comments and resubmit" |

## Events Triggered

- `PayrollRunCreated` → [[event-catalog]]
- `PayrollRunApproved` → [[event-catalog]]
- `PayslipGenerated` → [[event-catalog]]
- Notifications to employees → [[notification-system]]

## Related Flows

- [[payroll-provider-setup]] — provider configuration
- [[tax-configuration]] — tax rules
- [[allowance-setup]] — allowance types
- [[pension-configuration]] — pension deductions
- [[payroll-adjustment]] — post-run corrections
- [[payslip-view]] — employee views result

## Module References

- [[payroll-execution]]
- [[payroll-providers]]
- [[tax-configuration]]
- [[allowances]]
- [[pensions]]
- [[notification-system]]
