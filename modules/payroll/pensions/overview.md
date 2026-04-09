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

- [[modules/payroll/overview|Payroll Module]]
- [[frontend/architecture/overview|Payroll Execution]]
- [[frontend/architecture/overview|Tax Configuration]]
- [[frontend/architecture/overview|Allowances]]
- [[frontend/architecture/overview|Audit Trail]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[backend/shared-kernel|Shared Kernel]]
- Payroll task file (deferred to Phase 2)
