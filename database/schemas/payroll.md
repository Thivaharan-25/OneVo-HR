# Payroll — Schema

**Module:** [[modules/payroll/overview|Payroll]]
**Phase:** Phase 2
**Tables:** 11

---

## `allowance_types`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(100)` | e.g., "Transport", "Housing", "Meal" |
| `is_taxable` | `boolean` |  |
| `calculation_method` | `varchar(20)` | `fixed`, `percentage` |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `employee_allowances`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `employee_id` | `uuid` | FK → employees |
| `allowance_type_id` | `uuid` | FK → allowance_types |
| `amount` | `decimal(15,2)` |  |
| `effective_from` | `date` |  |
| `effective_to` | `date` |  |

**Foreign Keys:** `employee_id` → [[database/schemas/core-hr#`employees`|employees]], `allowance_type_id` → [[#`allowance_types`|allowance_types]]

---

## `employee_pension_enrollments`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `employee_id` | `uuid` | FK → employees |
| `pension_plan_id` | `uuid` | FK → pension_plans |
| `enrolled_at` | `date` |  |
| `opt_out_at` | `date` | Nullable |

**Foreign Keys:** `employee_id` → [[database/schemas/core-hr#`employees`|employees]], `pension_plan_id` → [[#`pension_plans`|pension_plans]]

---

## `payroll_adjustments`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `employee_id` | `uuid` | FK → employees |
| `payroll_run_id` | `uuid` | FK → payroll_runs |
| `type` | `varchar(20)` | `bonus`, `deduction`, `reimbursement`, `penalty` |
| `amount` | `decimal(15,2)` |  |
| `reason` | `varchar(255)` |  |

**Foreign Keys:** `employee_id` → [[database/schemas/core-hr#`employees`|employees]], `payroll_run_id` → [[#`payroll_runs`|payroll_runs]]

---

## `payroll_audit_trail`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `payroll_run_id` | `uuid` | FK → payroll_runs |
| `action` | `varchar(50)` |  |
| `performed_by_id` | `uuid` |  |
| `details_json` | `jsonb` |  |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `payroll_run_id` → [[#`payroll_runs`|payroll_runs]]

---

## `payroll_connections`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `provider_id` | `uuid` | FK → payroll_providers |
| `legal_entity_id` | `uuid` | FK → legal_entities |
| `config_json` | `jsonb` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `provider_id` → [[#`payroll_providers`|payroll_providers]], `legal_entity_id` → [[database/schemas/org-structure#`legal_entities`|legal_entities]]

---

## `payroll_providers`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `name` | `varchar(100)` |  |
| `provider_type` | `varchar(30)` | `internal`, `adp`, `oracle` |
| `credentials_encrypted` | `bytea` | Encrypted |
| `is_active` | `boolean` |  |

---

## `payroll_runs`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `legal_entity_id` | `uuid` | FK → legal_entities |
| `period_start` | `date` |  |
| `period_end` | `date` |  |
| `status` | `varchar(20)` | `draft`, `processing`, `completed`, `failed` |
| `total_gross` | `decimal(18,2)` |  |
| `total_net` | `decimal(18,2)` |  |
| `total_tax` | `decimal(18,2)` |  |
| `employee_count` | `int` |  |
| `executed_by_id` | `uuid` | FK → users |
| `executed_at` | `timestamptz` |  |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `legal_entity_id` → [[database/schemas/org-structure#`legal_entities`|legal_entities]], `executed_by_id` → [[database/schemas/infrastructure#`users`|users]]

---

## `payslips`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `payroll_run_id` | `uuid` | FK → payroll_runs |
| `employee_id` | `uuid` | FK → employees |
| `base_salary` | `decimal(15,2)` |  |
| `total_allowances` | `decimal(15,2)` |  |
| `total_deductions` | `decimal(15,2)` |  |
| `tax_amount` | `decimal(15,2)` |  |
| `pension_employee` | `decimal(15,2)` |  |
| `pension_employer` | `decimal(15,2)` |  |
| `net_pay` | `decimal(15,2)` |  |
| `worked_hours` | `decimal(7,2)` | From [[modules/workforce-presence/overview |
| `overtime_hours` | `decimal(7,2)` |  |
| `leave_days_deducted` | `decimal(5,1)` |  |
| `activity_active_hours` | `decimal(7,2)` | Read-only from activity-monitoring (informational, not used in calculation) |
| `activity_idle_hours` | `decimal(7,2)` | Read-only from activity-monitoring |
| `activity_meeting_hours` | `decimal(7,2)` | Read-only from activity-monitoring |
| `activity_active_pct` | `decimal(5,2)` | Read-only from activity-monitoring |
| `activity_top_apps_json` | `jsonb` | Read-only — top 5 apps for the period |
| `breakdown_json` | `jsonb` | Line-by-line breakdown |

**Foreign Keys:** `payroll_run_id` → [[#`payroll_runs`|payroll_runs]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]]

---

## `pension_plans`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(100)` |  |
| `employee_contribution_pct` | `decimal(5,2)` |  |
| `employer_contribution_pct` | `decimal(5,2)` |  |
| `is_mandatory` | `boolean` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `tax_configurations`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `country_id` | `uuid` | FK → countries |
| `tax_brackets_json` | `jsonb` | Progressive tax brackets |
| `effective_from` | `date` |  |

**Foreign Keys:** `country_id` → [[database/schemas/infrastructure#`countries`|countries]]

---

## Related

- [[modules/payroll/overview|Payroll Module]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]