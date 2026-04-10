# Module: Payroll

**Namespace:** `ONEVO.Modules.Payroll`
**Phase:** 2 — Deferred
**Pillar:** 1 — HR Management
**Owner:** Dev 3
**Tables:** 11

---

## Purpose

Manages payroll providers, tax engines, allowances, pensions, and batch payroll execution. Reads actual worked hours from [[modules/workforce-presence/overview|Workforce Presence]] (not just clock-in/out) and leave data from [[modules/leave/overview|Leave]] to compute payroll.

**Phase 1 activity data feed:** Payroll also reads activity data from [[modules/activity-monitoring/overview|Activity Monitoring]] as a **read-only reference** — active time, idle time, app usage summary, meeting time. This data is displayed alongside payroll data for context but does NOT affect salary calculation in Phase 1. It prepares the data pipeline for Phase 2 payroll integration.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[modules/core-hr/overview\|Core Hr]] | `IEmployeeService` | Employee salary, bank details |
| **Depends on** | [[modules/workforce-presence/overview\|Workforce Presence]] | `IWorkforcePresenceService` | Actual worked hours |
| **Depends on** | [[modules/leave/overview\|Leave]] | `ILeaveService` | Leave days for deductions |
| **Depends on** | [[modules/org-structure/overview\|Org Structure]] | `IOrgStructureService` | Legal entity context |
| **Depends on** | [[modules/activity-monitoring/overview\|Activity Monitoring]] | `IActivityMonitoringService` | Activity data feed (read-only): active/idle hours, app usage, meeting time |

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
| `worked_hours` | `decimal(7,2)` | From [[modules/workforce-presence/overview\|Workforce Presence]] |
| `overtime_hours` | `decimal(7,2)` | |
| `leave_days_deducted` | `decimal(5,1)` | |
| `activity_active_hours` | `decimal(7,2)` | Read-only from activity-monitoring (informational, not used in calculation) |
| `activity_idle_hours` | `decimal(7,2)` | Read-only from activity-monitoring |
| `activity_meeting_hours` | `decimal(7,2)` | Read-only from activity-monitoring |
| `activity_active_pct` | `decimal(5,2)` | Read-only from activity-monitoring |
| `activity_top_apps_json` | `jsonb` | Read-only — top 5 apps for the period |
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
4. **Activity data is read-only in Phase 1.** The `activity_*` columns on payslips are informational — they do NOT affect `net_pay` calculation. They provide visibility into employee work behaviour alongside payroll. Phase 2 will optionally use activity data for productivity-based adjustments.
5. **Activity data is populated during payroll run** by calling `IActivityMonitoringService.GetDailySummaryAsync()` for each day in the payroll period and aggregating. If activity monitoring is disabled for an employee, `activity_*` columns are null.

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
| GET | `/api/v1/payroll/activity-summary/{employeeId}` | `payroll:read` | Activity data feed for payroll period (active/idle hours, app usage, meeting time) |
| GET | `/api/v1/payroll/export/with-activity` | `payroll:read` | Export payroll data with activity columns (CSV/Excel) |

## Features

- [[modules/payroll/payroll-providers/overview|Payroll Providers]] — External payroll system connections (ADP, Oracle, internal)
- [[Userflow/Payroll/tax-configuration|Tax Configuration]] — Country-specific progressive tax bracket definitions
- [[modules/payroll/allowances/overview|Allowances]] — Allowance types and per-employee assignments
- [[modules/payroll/pensions/overview|Pensions]] — Pension plan definitions and employee enrollments
- [[modules/payroll/payroll-execution/overview|Payroll Execution]] — Batch payroll run with pessimistic locking — frontend: [[modules/payroll/payroll-execution/frontend|Frontend]]
- [[modules/payroll/adjustments/overview|Adjustments]] — Bonuses, deductions, reimbursements, penalties per run
- [[modules/payroll/audit-trail/overview|Audit Trail]] — Payroll audit trail with performed-by tracking

---

## Related

- [[infrastructure/multi-tenancy|Multi Tenancy]] — All payroll data is tenant-scoped
- [[security/compliance|Compliance]] — Payroll audit trail for legal record-keeping
- [[security/data-classification|Data Classification]] — Provider credentials encrypted at rest
- [[backend/messaging/error-handling|Error Handling]] — `SELECT FOR UPDATE` pessimistic locking prevents concurrent runs
- Payroll task file (deferred to Phase 2) — Implementation task file

See also: [[backend/module-catalog|Module Catalog]], [[modules/core-hr/overview|Core Hr]], [[modules/workforce-presence/overview|Workforce Presence]], [[modules/leave/overview|Leave]]
