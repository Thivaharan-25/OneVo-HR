# Module: Payroll

**Namespace:** `ONEVO.Modules.Payroll`
**Pillar:** 1 — HR Management
**Owner:** Dev 3 (Week 4)
**Tables:** 11
**Task File:** [[WEEK4-payroll]]

---

## Purpose

Manages payroll providers, tax engines, allowances, pensions, and batch payroll execution. Reads actual worked hours from [[workforce-presence]] (not just clock-in/out) and leave data from [[leave]] to compute payroll.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[core-hr]] | `IEmployeeService` | Employee salary, bank details |
| **Depends on** | [[workforce-presence]] | `IWorkforcePresenceService` | Actual worked hours |
| **Depends on** | [[leave]] | `ILeaveService` | Leave days for deductions |
| **Depends on** | [[org-structure]] | `IOrgStructureService` | Legal entity context |

---

## Public Interface

```csharp
public interface IPayrollService
{
    Task<Result<PayrollRunDto>> ExecutePayrollRunAsync(ExecutePayrollCommand command, CancellationToken ct);
    Task<Result<PayrollRunDto>> GetPayrollRunAsync(Guid runId, CancellationToken ct);
    Task<Result<List<PayslipDto>>> GetPayslipsAsync(Guid employeeId, int year, CancellationToken ct);
}
```

---

## Database Tables (11)

### `payroll_providers`

External payroll system connections.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `name` | `varchar(100)` | |
| `provider_type` | `varchar(30)` | `internal`, `adp`, `oracle` |
| `credentials_encrypted` | `bytea` | Encrypted |
| `is_active` | `boolean` | |

### `payroll_connections`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `provider_id` | `uuid` | FK → payroll_providers |
| `legal_entity_id` | `uuid` | FK → legal_entities |
| `config_json` | `jsonb` | |

### `tax_configurations`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `country_id` | `uuid` | FK → countries |
| `tax_brackets_json` | `jsonb` | Progressive tax brackets |
| `effective_from` | `date` | |

### `allowance_types`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(100)` | e.g., "Transport", "Housing", "Meal" |
| `is_taxable` | `boolean` | |
| `calculation_method` | `varchar(20)` | `fixed`, `percentage` |

### `employee_allowances`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `employee_id` | `uuid` | FK → employees |
| `allowance_type_id` | `uuid` | FK → allowance_types |
| `amount` | `decimal(15,2)` | |
| `effective_from` | `date` | |
| `effective_to` | `date` | |

### `pension_plans`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(100)` | |
| `employee_contribution_pct` | `decimal(5,2)` | |
| `employer_contribution_pct` | `decimal(5,2)` | |
| `is_mandatory` | `boolean` | |

### `employee_pension_enrollments`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `employee_id` | `uuid` | FK → employees |
| `pension_plan_id` | `uuid` | FK → pension_plans |
| `enrolled_at` | `date` | |
| `opt_out_at` | `date` | Nullable |

### `payroll_runs`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `legal_entity_id` | `uuid` | FK → legal_entities |
| `period_start` | `date` | |
| `period_end` | `date` | |
| `status` | `varchar(20)` | `draft`, `processing`, `completed`, `failed` |
| `total_gross` | `decimal(18,2)` | |
| `total_net` | `decimal(18,2)` | |
| `total_tax` | `decimal(18,2)` | |
| `employee_count` | `int` | |
| `executed_by_id` | `uuid` | FK → users |
| `executed_at` | `timestamptz` | |
| `created_at` | `timestamptz` | |

**Pessimistic locking:** Uses `SELECT FOR UPDATE` — never run payroll in parallel for the same tenant. Use Hangfire distributed lock.

### `payslips`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `payroll_run_id` | `uuid` | FK → payroll_runs |
| `employee_id` | `uuid` | FK → employees |
| `base_salary` | `decimal(15,2)` | |
| `total_allowances` | `decimal(15,2)` | |
| `total_deductions` | `decimal(15,2)` | |
| `tax_amount` | `decimal(15,2)` | |
| `pension_employee` | `decimal(15,2)` | |
| `pension_employer` | `decimal(15,2)` | |
| `net_pay` | `decimal(15,2)` | |
| `worked_hours` | `decimal(7,2)` | From [[workforce-presence]] |
| `overtime_hours` | `decimal(7,2)` | |
| `leave_days_deducted` | `decimal(5,1)` | |
| `breakdown_json` | `jsonb` | Line-by-line breakdown |

### `payroll_adjustments`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `employee_id` | `uuid` | FK → employees |
| `payroll_run_id` | `uuid` | FK → payroll_runs |
| `type` | `varchar(20)` | `bonus`, `deduction`, `reimbursement`, `penalty` |
| `amount` | `decimal(15,2)` | |
| `reason` | `varchar(255)` | |

### `payroll_audit_trail`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `payroll_run_id` | `uuid` | FK → payroll_runs |
| `action` | `varchar(50)` | |
| `performed_by_id` | `uuid` | |
| `details_json` | `jsonb` | |
| `created_at` | `timestamptz` | |

---

## Key Business Rules

1. **Payroll reads actual hours from `IWorkforcePresenceService`** — not just clock-in/out times.
2. **Pessimistic locking** via `SELECT FOR UPDATE` — prevents concurrent payroll runs for the same tenant.
3. **`tenant_id`** is used consistently on all tables — no column mapping workarounds needed.

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/payroll/runs` | `payroll:read` | List payroll runs |
| POST | `/api/v1/payroll/runs` | `payroll:run` | Execute payroll run |
| PUT | `/api/v1/payroll/runs/{id}/approve` | `payroll:approve` | Approve payroll |
| GET | `/api/v1/payroll/payslips/{employeeId}` | `payroll:read` | Employee payslips |
| GET | `/api/v1/payroll/providers` | `payroll:read` | List providers |
| POST | `/api/v1/payroll/allowance-types` | `payroll:write` | Create allowance type |
| GET | `/api/v1/payroll/tax-config` | `payroll:read` | Tax configuration |

## Features

- [[payroll-providers]] — External payroll system connections (ADP, Oracle, internal)
- [[tax-configuration]] — Country-specific progressive tax bracket definitions
- [[allowances]] — Allowance types and per-employee assignments
- [[pensions]] — Pension plan definitions and employee enrollments
- [[payroll-execution]] — Batch payroll run with pessimistic locking — frontend: [[payroll-execution/frontend]]
- [[adjustments]] — Bonuses, deductions, reimbursements, penalties per run
- [[audit-trail]] — Payroll audit trail with performed-by tracking

---

## Related

- [[multi-tenancy]] — All payroll data is tenant-scoped
- [[compliance]] — Payroll audit trail for legal record-keeping
- [[data-classification]] — Provider credentials encrypted at rest
- [[error-handling]] — `SELECT FOR UPDATE` pessimistic locking prevents concurrent runs
- [[WEEK4-payroll]] — Implementation task file

See also: [[module-catalog]], [[core-hr]], [[workforce-presence]], [[leave]]
