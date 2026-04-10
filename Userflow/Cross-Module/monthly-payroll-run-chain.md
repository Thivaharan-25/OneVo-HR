# Monthly Payroll Run — Cross-Module Chain

**Area:** Cross-Module Scenario  
**Trigger:** Scheduled payroll run date (system-scheduled) or manual trigger by HR Admin  
**Required Permission(s):** `payroll:run`, `payroll:approve`, `attendance:read`, `leave:read`  
**Modules Involved:** Payroll, Workforce-Presence, Leave, Employee-Management, Expense, Documents, Notifications

---

## Context

Payroll doesn't just "run salaries." It must collect data from attendance (overtime, absences), leave (unpaid leave deductions), expense (reimbursements), and employee management (new hires, terminations, salary changes). This doc maps every data source that feeds into a payroll run and the outputs it produces.

## Preconditions

- Payroll provider configured → [[Userflow/Payroll/payroll-provider-setup|Payroll Provider Setup]]
- Tax rules configured for all employee countries → [[Userflow/Payroll/tax-configuration|Tax Configuration]]
- Attendance data finalized for the period (no pending corrections) → [[Userflow/Workforce-Presence/attendance-correction|Attendance Correction]]
- Leave data finalized (no pending approvals affecting payroll) → [[Userflow/Leave/leave-approval|Leave Approval]]
- Expense claims approved for the period → [[Userflow/Expense/expense-approval|Expense Approval]]

---

## Chain Reaction Flow

### Phase 1: Data Collection (Before Run)

| Order | Module | What Happens | Data Collected |
|:------|:-------|:-------------|:---------------|
| 1 | **Workforce-Presence** | Attendance summary pulled for pay period: total hours, overtime hours, absences, late arrivals | Hours worked, overtime, unpaid absences |
| 2 | **Leave** | Leave records pulled: unpaid leave days, leave encashment requests | Unpaid deductions, encashment additions |
| 3 | **Employee-Management** | Employee changes pulled: new hires (pro-rated), terminations (final pay), salary revisions, promotions | Salary base, pro-ration factors, final settlement flags |
| 4 | **Expense** | Approved expense claims pulled for reimbursement | Reimbursement amounts |
| 5 | **Payroll** | Recurring allowances and deductions applied (housing, transport, loan repayments, pension contributions) | Fixed additions/deductions |

### Phase 2: Payroll Calculation

| Order | Module | What Happens | Event Published |
|:------|:-------|:-------------|:----------------|
| 6 | **Payroll** | Gross pay calculated: base salary + overtime + allowances + reimbursements - unpaid leave | `PayrollCalculationCompleted` |
| 7 | **Payroll** | Tax calculated based on employee's country/entity tax rules. Pension contributions calculated | `TaxCalculationCompleted` |
| 8 | **Payroll** | Net pay calculated. Payroll summary generated for review | `PayrollRunReady` |

### Phase 3: Review & Approval

| Order | Module | What Happens | Event Published |
|:------|:-------|:-------------|:----------------|
| 9 | **Notifications** | HR Admin notified that payroll run is ready for review | `NotificationSent` |
| 10 | **Payroll** | HR Admin reviews payroll summary: headcount, total gross, total net, variance from last month | — |
| 11 | **Payroll** | HR Admin approves payroll run | `PayrollRunApproved` |

### Phase 4: Post-Approval Outputs

| Order | Module | What Happens | Event Published |
|:------|:-------|:-------------|:----------------|
| 12 | **Payroll** | Bank file generated for bulk payment processing | `BankFileGenerated` |
| 13 | **Documents** | Payslips generated (PDF) per employee, stored in employee's document folder | `PayslipsGenerated` |
| 14 | **Notifications** | Employees notified that payslip is available | `NotificationSent` |
| 15 | **Leave** | Leave encashment balances updated (if any encashments were processed) | `LeaveBalanceUpdated` |
| 16 | **Payroll** | Payroll run status set to `completed`. Audit trail recorded | `PayrollRunCompleted` |

---

## Dependency Chain

```
Data Collection (Steps 1-5) — all independent, run in parallel
│
Payroll Calculation (Steps 6-8) — sequential, needs all data from Steps 1-5
│
Review & Approval (Steps 9-11) — sequential
│
Post-Approval (Steps 12-16)
├── Bank file (Step 12) — independent
├── Payslips (Step 13) — independent
├── Employee notifications (Step 14) — needs Step 13
├── Leave balance update (Step 15) — independent
└── Audit trail (Step 16) — runs last
```

---

## What If a Step Fails?

| Failed Step | Impact | Recovery |
|:------------|:-------|:---------|
| Attendance data incomplete | Payroll uses last confirmed data; flagged for review | HR finalizes attendance, re-runs calculation |
| Leave data has pending approvals | Unpaid leave deductions may be incorrect | Manager completes approvals, HR re-runs |
| Employee salary change not captured | Employee paid at old rate | HR applies [[Userflow/Payroll/payroll-adjustment\|Payroll Adjustment]] in next run |
| Payslip generation fails | Employee can't view payslip | Admin re-triggers from [[Userflow/Documents/template-management\|Template Management]] |
| Bank file generation fails | Payment delayed | Admin retries; payroll status stays `approved` until bank file succeeds |

---

## Related Individual Flows

- [[Userflow/Payroll/payroll-run-execution|Payroll Run Execution]] — detailed run steps
- [[Userflow/Payroll/payroll-adjustment|Payroll Adjustment]] — post-run corrections
- [[Userflow/Payroll/payslip-view|Payslip View]] — employee views payslip
- [[Userflow/Workforce-Presence/overtime-management|Overtime Management]] — overtime data source
- [[Userflow/Leave/leave-cancellation|Leave Cancellation]] — late cancellations affecting payroll
- [[Userflow/Expense/expense-approval|Expense Approval]] — reimbursement data source
- [[Userflow/Cross-Module/employee-full-offboarding|Employee Full Offboarding]] — final settlement context

## Module References

- [[modules/payroll/overview|Payroll]]
- [[modules/leave/overview|Leave]]
- [[modules/core-hr/employee-profiles/overview|Employee Profiles]]
- [[modules/documents/overview|Documents]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/notification-system|Notification System]]
