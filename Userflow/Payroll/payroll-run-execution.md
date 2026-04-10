# Payroll Run Execution

**Area:** Payroll  
**Trigger:** Scheduled payroll date reached or HR Admin manually triggers run (scheduled or user action)
**Required Permission(s):** `payroll:run` (execute) + `payroll:approve` (final approval)  
**Related Permissions:** `payroll:read` (view results), `employees:read` (verify employee data)

---

## Preconditions

- Payroll provider configured → [[Userflow/Payroll/payroll-provider-setup|Payroll Provider Setup]]
- Tax rules set → [[Userflow/Payroll/tax-configuration|Tax Configuration]]
- Employee compensation records exist → [[Userflow/Employee-Management/compensation-setup|Compensation Setup]]
- Leave and attendance data up to date → [[Userflow/Leave/leave-approval|Leave Approval]], [[Userflow/Workforce-Presence/presence-session-view|Presence Session View]]
- Required permissions: [[Userflow/Auth-Access/permission-assignment|Permission Assignment Flow]]

## Flow Steps

### Step 1: Create Payroll Run
- **UI:** Payroll → Runs → "Create Run" → select pay period (e.g., March 2026) → select legal entity → click "Calculate"
- **API:** `POST /api/v1/payroll/runs`
- **Backend:** PayrollRunService.InitiateAsync() → [[modules/payroll/payroll-execution/overview|Payroll Execution]]

### Step 2: System Calculates (Automated via Hangfire)
- **Backend:** For each employee in legal entity:
  1. **Gross Salary** = base salary (prorated if mid-month join/leave)
  2. **+ Allowances** = housing + transport + meal + other → [[modules/payroll/allowances/overview|Allowances]]
  3. **+ Overtime** = approved overtime hours × overtime rate → [[Userflow/Workforce-Presence/overtime-management|Overtime Management]]
  4. **+ Expense Reimbursements** = approved expense claims → [[Userflow/Expense/expense-approval|Expense Approval]]
  5. **- Unpaid Leave** = unpaid leave days × daily rate → [[Userflow/Leave/leave-approval|Leave Approval]]
  6. **- Tax** = income tax from brackets → [[Userflow/Payroll/tax-configuration|Tax Configuration]]
  7. **- Pension (employee)** = contribution % → [[Userflow/Payroll/pension-configuration|Pension Configuration]]
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
  1. Payslips generated (PDF) per employee → [[modules/documents/document-management/overview|Document Management]]
  2. Employees notified → [[backend/notification-system|Notification System]]
  3. Provider sync triggered (if external provider) → [[Userflow/Payroll/payroll-provider-setup|Payroll Provider Setup]]
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

- `PayrollRunCreated` → [[backend/messaging/event-catalog|Event Catalog]]
- `PayrollRunApproved` → [[backend/messaging/event-catalog|Event Catalog]]
- `PayslipGenerated` → [[backend/messaging/event-catalog|Event Catalog]]
- Notifications to employees → [[backend/notification-system|Notification System]]

## Related Flows

- [[Userflow/Payroll/payroll-provider-setup|Payroll Provider Setup]] — provider configuration
- [[Userflow/Payroll/tax-configuration|Tax Configuration]] — tax rules
- [[Userflow/Payroll/allowance-setup|Allowance Setup]] — allowance types
- [[Userflow/Payroll/pension-configuration|Pension Configuration]] — pension deductions
- [[Userflow/Payroll/payroll-adjustment|Payroll Adjustment]] — post-run corrections
- [[Userflow/Payroll/payslip-view|Payslip View]] — employee views result

## Module References

- [[modules/payroll/payroll-execution/overview|Payroll Execution]]
- [[modules/payroll/payroll-providers/overview|Payroll Providers]]
- [[Userflow/Payroll/tax-configuration|Tax Configuration]]
- [[modules/payroll/allowances/overview|Allowances]]
- [[modules/payroll/pensions/overview|Pensions]]
- [[backend/notification-system|Notification System]]
