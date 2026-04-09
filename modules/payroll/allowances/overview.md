# Allowances

**Module:** Payroll  
**Feature:** Allowances

---

## Purpose

Manages allowance types and employee allowance assignments.

## Database Tables

### `allowance_types`
Fields: `name` (Transport, Housing, Meal), `is_taxable`, `calculation_method` (`fixed`, `percentage`).

### `employee_allowances`
Fields: `employee_id`, `allowance_type_id`, `amount`, `effective_from`, `effective_to`.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| POST | `/api/v1/payroll/allowance-types` | `payroll:write` | Create allowance type |

## Related

- [[modules/payroll/overview|Payroll Module]]
- [[frontend/architecture/overview|Payroll Execution]]
- [[frontend/architecture/overview|Adjustments]]
- [[frontend/architecture/overview|Tax Configuration]]
- [[frontend/architecture/overview|Pensions]]
- [[frontend/architecture/overview|Audit Trail]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[backend/shared-kernel|Shared Kernel]]
- Payroll task file (deferred to Phase 2)
