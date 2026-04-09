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

- [[modules/payroll/overview|Payroll Module]]
- [[frontend/architecture/overview|Payroll Execution]]
- [[frontend/architecture/overview|Adjustments]]
- [[frontend/architecture/overview|Allowances]]
- [[frontend/architecture/overview|Tax Configuration]]
- [[frontend/architecture/overview|Pensions]]
- [[frontend/architecture/overview|Payroll Providers]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[security/data-classification|Data Classification]]
- [[database/migration-patterns|Migration Patterns]]
- [[backend/shared-kernel|Shared Kernel]]
- Payroll task file (deferred to Phase 2)
