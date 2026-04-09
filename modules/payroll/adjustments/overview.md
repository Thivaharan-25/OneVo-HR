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

- [[modules/payroll/overview|Payroll Module]]
- [[frontend/architecture/overview|Payroll Execution]]
- [[frontend/architecture/overview|Allowances]]
- [[frontend/architecture/overview|Audit Trail]]
- [[frontend/architecture/overview|Tax Configuration]]
- [[frontend/architecture/overview|Pensions]]
- [[frontend/architecture/overview|Payroll Providers]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[backend/shared-kernel|Shared Kernel]]
- Payroll task file (deferred to Phase 2)
