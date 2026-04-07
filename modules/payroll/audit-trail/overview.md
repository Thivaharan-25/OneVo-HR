# Payroll Audit Trail

**Module:** Payroll  
**Feature:** Audit Trail

---

## Purpose

Append-only audit trail for all payroll actions.

## Database Tables

### `payroll_audit_trail`
Fields: `payroll_run_id`, `action`, `performed_by_id`, `details_json`, `created_at`.

## Related

- [[payroll|Payroll Module]]
- [[payroll/payroll-execution/overview|Payroll Execution]]
- [[payroll/adjustments/overview|Adjustments]]
- [[payroll/allowances/overview|Allowances]]
- [[payroll/tax-configuration/overview|Tax Configuration]]
- [[payroll/pensions/overview|Pensions]]
- [[payroll/payroll-providers/overview|Payroll Providers]]
- [[multi-tenancy]]
- [[auth-architecture]]
- [[data-classification]]
- [[migration-patterns]]
- [[shared-kernel]]
- [[WEEK4-payroll]]
