# Payroll Execution

**Module:** Payroll  
**Feature:** Payroll Execution

---

## Purpose

Batch payroll run execution producing payslips. Uses pessimistic locking (`SELECT FOR UPDATE`) to prevent concurrent runs.

## Database Tables

### `payroll_runs`
Fields: `legal_entity_id`, `period_start`, `period_end`, `status` (`draft`, `processing`, `completed`, `failed`), `total_gross`, `total_net`, `total_tax`, `employee_count`.

### `payslips`
Fields: `payroll_run_id`, `employee_id`, `base_salary`, `total_allowances`, `total_deductions`, `tax_amount`, `pension_employee`, `pension_employer`, `net_pay`, `worked_hours` (from workforce-presence), `overtime_hours`, `leave_days_deducted`, `breakdown_json`.

## Key Business Rules

1. Reads actual hours from `IWorkforcePresenceService`.
2. Pessimistic locking via `SELECT FOR UPDATE` — never run in parallel for same tenant.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/payroll/runs` | `payroll:read` | List runs |
| POST | `/api/v1/payroll/runs` | `payroll:run` | Execute run |
| PUT | `/api/v1/payroll/runs/{id}/approve` | `payroll:approve` | Approve |
| GET | `/api/v1/payroll/payslips/{employeeId}` | `payroll:read` | Payslips |

## Related

- [[modules/payroll/overview|Payroll Module]]
- [[frontend/architecture/overview|Adjustments]]
- [[frontend/architecture/overview|Allowances]]
- [[frontend/architecture/overview|Audit Trail]]
- [[frontend/architecture/overview|Tax Configuration]]
- [[frontend/architecture/overview|Pensions]]
- [[frontend/architecture/overview|Payroll Providers]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[backend/messaging/error-handling|Error Handling]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[backend/shared-kernel|Shared Kernel]]
- Payroll task file (deferred to Phase 2)
