# Leave — Schema

**Module:** [[modules/leave/overview|Leave]]
**Phase:** Phase 1
**Tables:** 5

---

## `leave_balances_audit`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `employee_id` | `uuid` | FK → employees |
| `leave_type_id` | `uuid` | FK → leave_types |
| `change_type` | `varchar(20)` | `accrual`, `deduction`, `carry_forward`, `forfeiture`, `adjustment` |
| `days_changed` | `decimal(5,1)` | Positive or negative |
| `balance_after` | `decimal(5,1)` |  |
| `reason` | `varchar(255)` |  |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `employee_id` → [[database/schemas/core-hr#`employees`|employees]], `leave_type_id` → [[#`leave_types`|leave_types]]

---

## `leave_entitlements`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `employee_id` | `uuid` | FK → employees |
| `leave_type_id` | `uuid` | FK → leave_types |
| `year` | `int` |  |
| `total_days` | `decimal(5,1)` | Based on policy + proration |
| `used_days` | `decimal(5,1)` | Updated on approval |
| `carried_forward_days` | `decimal(5,1)` | From previous year |
| `remaining_days` | `decimal(5,1)` | Computed |

**Foreign Keys:** `employee_id` → [[database/schemas/core-hr#`employees`|employees]], `leave_type_id` → [[#`leave_types`|leave_types]]

---

## `leave_policies`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `leave_type_id` | `uuid` | FK → leave_types |
| `country_id` | `uuid` | FK → countries (nullable — global) |
| `job_level_id` | `uuid` | FK → job_levels (nullable — all levels) |
| `annual_entitlement_days` | `decimal(5,1)` |  |
| `carry_forward_max_days` | `decimal(5,1)` |  |
| `carry_forward_expiry_months` | `int` |  |
| `accrual_method` | `varchar(20)` | `annual`, `monthly`, `daily` |
| `proration_method` | `varchar(20)` | `calendar_days`, `working_days` |
| `superseded_by_id` | `uuid` | Self-referencing — versioning chain |
| `effective_from` | `date` |  |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `leave_type_id` → [[#`leave_types`|leave_types]], `country_id` → [[database/schemas/infrastructure#`countries`|countries]], `job_level_id` → [[database/schemas/org-structure#`job_levels`|job_levels]]

---

## `leave_requests`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `employee_id` | `uuid` | FK → employees |
| `leave_type_id` | `uuid` | FK → leave_types |
| `start_date` | `date` |  |
| `end_date` | `date` |  |
| `total_days` | `decimal(5,1)` | Excluding weekends/holidays |
| `reason` | `text` |  |
| `status` | `varchar(20)` | `pending`, `approved`, `rejected`, `cancelled` |
| `approved_by_id` | `uuid` | FK → users |
| `approved_at` | `timestamptz` |  |
| `conflict_snapshot_json` | `jsonb` | Calendar conflicts at submission time (nullable) — see [[Userflow/Calendar/conflict-detection |
| `document_file_id` | `uuid` | FK → file_records (nullable) |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `employee_id` → [[database/schemas/core-hr#`employees`|employees]], `leave_type_id` → [[#`leave_types`|leave_types]], `approved_by_id` → [[database/schemas/infrastructure#`users`|users]], `document_file_id` → [[database/schemas/infrastructure#`file_records`|file_records]]

---

## `leave_types`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(50)` | e.g., "Annual", "Sick", "Maternity" |
| `is_paid` | `boolean` |  |
| `requires_approval` | `boolean` |  |
| `requires_document` | `boolean` | Medical certificate etc. |
| `max_consecutive_days` | `int` | Nullable |
| `is_active` | `boolean` |  |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]]

---

## Related

- [[modules/leave/overview|Leave Module]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]