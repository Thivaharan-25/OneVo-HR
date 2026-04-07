# Pensions

**Module:** Payroll  
**Feature:** Pensions

---

## Purpose

Pension plan definitions and employee enrollment.

## Database Tables

### `pension_plans`
Fields: `name`, `employee_contribution_pct`, `employer_contribution_pct`, `is_mandatory`.

### `employee_pension_enrollments`
Fields: `employee_id`, `pension_plan_id`, `enrolled_at`, `opt_out_at`.

## Related

- [[payroll|Payroll Module]]
- [[payroll/payroll-execution/overview|Payroll Execution]]
- [[payroll/tax-configuration/overview|Tax Configuration]]
- [[payroll/allowances/overview|Allowances]]
- [[payroll/audit-trail/overview|Audit Trail]]
- [[multi-tenancy]]
- [[auth-architecture]]
- [[shared-kernel]]
- [[WEEK4-payroll]]
