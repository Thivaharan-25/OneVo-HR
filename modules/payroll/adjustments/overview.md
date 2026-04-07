# Payroll Adjustments

**Module:** Payroll  
**Feature:** Adjustments

---

## Purpose

Per-employee adjustments within a payroll run (bonuses, deductions, reimbursements, penalties).

## Database Tables

### `payroll_adjustments`
Fields: `employee_id`, `payroll_run_id`, `type` (`bonus`, `deduction`, `reimbursement`, `penalty`), `amount`, `reason`.

## Related

- [[payroll|Payroll Module]]
- [[payroll/payroll-execution/overview|Payroll Execution]]
- [[payroll/allowances/overview|Allowances]]
- [[payroll/audit-trail/overview|Audit Trail]]
- [[payroll/tax-configuration/overview|Tax Configuration]]
- [[payroll/pensions/overview|Pensions]]
- [[payroll/payroll-providers/overview|Payroll Providers]]
- [[multi-tenancy]]
- [[auth-architecture]]
- [[shared-kernel]]
- [[WEEK4-payroll]]
