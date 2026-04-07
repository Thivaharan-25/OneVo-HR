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

- [[payroll|Payroll Module]]
- [[payroll/payroll-execution/overview|Payroll Execution]]
- [[payroll/adjustments/overview|Adjustments]]
- [[payroll/tax-configuration/overview|Tax Configuration]]
- [[payroll/pensions/overview|Pensions]]
- [[payroll/audit-trail/overview|Audit Trail]]
- [[multi-tenancy]]
- [[auth-architecture]]
- [[shared-kernel]]
- [[WEEK4-payroll]]
