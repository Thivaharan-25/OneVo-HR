# Core HR â€” Schema

**Module:** [[modules/core-hr/overview|Core HR]]
**Phase:** Phase 1
**Tables:** 15

---

## `employee_addresses`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `employee_id` | `uuid` | FK â†’ employees |
| `address_type` | `varchar(20)` | `permanent`, `current`, `emergency` |
| `address_json` | `jsonb` | Street, city, state, postal, country |
| `is_primary` | `boolean` |  |

**Foreign Keys:** `employee_id` â†’ [[#`employees`|employees]]

---

## `employee_bank_details`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `employee_id` | `uuid` | FK â†’ employees |
| `bank_name` | `varchar(100)` |  |
| `branch_name` | `varchar(100)` |  |
| `account_number_encrypted` | `bytea` | **Encrypted** via `IEncryptionService` (AES-256) |
| `routing_number` | `varchar(20)` |  |
| `is_primary` | `boolean` |  |

**Foreign Keys:** `employee_id` â†’ [[#`employees`|employees]]

---

## `employee_custom_fields`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `employee_id` | `uuid` | FK â†’ employees |
| `field_name` | `varchar(100)` |  |
| `field_value` | `text` |  |
| `field_type` | `varchar(20)` | `text`, `number`, `date`, `boolean`, `select` |

**Foreign Keys:** `employee_id` â†’ [[#`employees`|employees]]

---

## `employee_dependents`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `employee_id` | `uuid` | FK â†’ employees |
| `name` | `varchar(100)` |  |
| `relationship` | `varchar(20)` | `spouse`, `child`, `parent`, `other` |
| `date_of_birth` | `date` |  |
| `is_emergency_contact` | `boolean` |  |
| `phone` | `varchar(20)` |  |

**Foreign Keys:** `employee_id` â†’ [[#`employees`|employees]]

---

## `employee_emergency_contacts`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `employee_id` | `uuid` | FK â†’ employees |
| `name` | `varchar(100)` |  |
| `relationship` | `varchar(30)` |  |
| `phone` | `varchar(20)` |  |
| `email` | `varchar(255)` |  |
| `is_primary` | `boolean` |  |

**Foreign Keys:** `employee_id` â†’ [[#`employees`|employees]]

---

## `employee_lifecycle_events`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `employee_id` | `uuid` | FK â†’ employees |
| `event_type` | `varchar(30)` | `hired`, `promoted`, `transferred`, `salary_change`, `suspended`, `terminated`, `resigned` |
| `event_date` | `date` |  |
| `details_json` | `jsonb` | Event-specific data |
| `performed_by_id` | `uuid` | FK â†’ users |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `employee_id` â†’ [[#`employees`|employees]], `performed_by_id` â†’ [[database/schemas/infrastructure#`users`|users]]

---

## `employee_qualifications`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `employee_id` | `uuid` | FK â†’ employees |
| `qualification_type` | `varchar(20)` | `degree`, `certification`, `license` |
| `title` | `varchar(200)` |  |
| `institution` | `varchar(200)` |  |
| `year_obtained` | `int` |  |
| `expiry_date` | `date` | Nullable |
| `document_file_id` | `uuid` | FK â†’ file_records |

**Foreign Keys:** `employee_id` â†’ [[#`employees`|employees]], `document_file_id` â†’ [[database/schemas/infrastructure#`file_records`|file_records]]

---

## `employee_salary_history`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `employee_id` | `uuid` | FK â†’ employees |
| `effective_date` | `date` |  |
| `base_salary` | `decimal(15,2)` |  |
| `currency_code` | `varchar(3)` |  |
| `change_reason` | `varchar(100)` | `hire`, `promotion`, `annual_review`, `adjustment` |
| `approved_by_id` | `uuid` | FK â†’ users |

**Foreign Keys:** `employee_id` â†’ [[#`employees`|employees]], `approved_by_id` â†’ [[database/schemas/infrastructure#`users`|users]]

---

## `employee_work_history`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `employee_id` | `uuid` | FK â†’ employees |
| `company_name` | `varchar(200)` |  |
| `job_title` | `varchar(100)` |  |
| `start_date` | `date` |  |
| `end_date` | `date` |  |
| `reason_for_leaving` | `varchar(255)` |  |

**Foreign Keys:** `employee_id` â†’ [[#`employees`|employees]]

---

## `employees`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK â†’ tenants |
| `user_id` | `uuid` | FK â†’ users (1:1) |
| `employee_number` | `varchar(20)` | Unique per tenant |
| `first_name` | `varchar(100)` |  |
| `last_name` | `varchar(100)` |  |
| `email` | `varchar(255)` | Work email |
| `phone` | `varchar(20)` |  |
| `date_of_birth` | `date` | PII â€” CONFIDENTIAL |
| `gender` | `varchar(10)` |  |
| `nationality_id` | `uuid` | FK â†’ countries |
| `department_id` | `uuid` | FK -> departments, nullable; current profile snapshot derived from active position when available |
| `legal_entity_id` | `uuid` | FK â†’ legal_entities |
| `employment_type` | `varchar(20)` | `full_time`, `part_time`, `contract`, `intern` |
| `employment_status` | `varchar(20)` | `active`, `on_leave`, `suspended`, `terminated`, `resigned` |
| `work_mode` | `varchar(10)` | `office`, `remote`, `hybrid` |
| `hire_date` | `date` |  |
| `probation_end_date` | `date` | Nullable |
| `termination_date` | `date` | Nullable |
| `avatar_file_id` | `uuid` | FK â†’ file_records |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |
| `is_deleted` | `boolean` | Soft delete |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `user_id` -> [[database/schemas/infrastructure#`users`|users]], `nationality_id` -> [[database/schemas/infrastructure#`countries`|countries]], `department_id` -> [[database/schemas/org-structure#`departments`|departments]], `legal_entity_id` -> [[database/schemas/org-structure#`legal_entities`|legal_entities]], `avatar_file_id` -> [[database/schemas/infrastructure#`file_records`|file_records]]
---

## `employee_assignment_history`

Effective-dated assignment history for department and position snapshots. Reporting history is resolved from `position_assignments` and the position hierarchy, not from an employee-level manager field.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `department_id` | `uuid` | FK -> departments, nullable |
| `position_id` | `uuid` | FK -> positions, nullable |
| `effective_from` | `date` | Start date for this assignment |
| `effective_to` | `date` | Nullable. Null means current open assignment |

---

## `employee_transfers`

Workflow/request record for employee transfer. Approved transfers update current employee fields and close/create `employee_assignment_history` rows on effective date.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `from_department_id` | `uuid` | nullable |
| `to_department_id` | `uuid` | nullable |
| `from_position_id` | `uuid` | nullable |
| `to_position_id` | `uuid` | nullable |
| `effective_date` | `date` | When approved transfer becomes active |
| `status` | `varchar(30)` | `Pending`, `Approved`, `Rejected`, `Cancelled`, `Applied` |
| `reason` | `varchar(500)` | Business reason |
| `requested_by_id` | `uuid` | FK -> users |
| `approved_by_id` | `uuid` | FK -> users, nullable |


## `offboarding_records`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `employee_id` | `uuid` | FK â†’ employees |
| `reason` | `varchar(30)` | `resignation`, `termination`, `retirement`, `contract_end` |
| `last_working_date` | `date` |  |
| `knowledge_risk_level` | `varchar(10)` | `low`, `medium`, `high`, `critical` |
| `exit_interview_notes` | `text` |  |
| `penalties_json` | `jsonb` | Outstanding loans, notice period, asset recovery, knowledge-transfer bypass penalties, etc. |
| `status` | `varchar(20)` | `initiated`, `in_progress`, `completed` |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `employee_id` â†’ [[#`employees`|employees]]

---

`penalties_json` recommended shape:

```json
{
  "items": [
    {
      "type": "knowledge_transfer_bypass",
      "amount": 0,
      "currency": "USD",
      "reason": "Critical handover skipped with HR approval",
      "approved_by_id": "uuid",
      "approved_at": "2026-04-29T00:00:00Z",
      "source": "offboarding_workflow"
    }
  ],
  "total_amount": 0,
  "currency": "USD"
}
```

## `onboarding_tasks`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `employee_id` | `uuid` | FK â†’ employees |
| `task_name` | `varchar(200)` |  |
| `category` | `varchar(50)` | `documentation`, `equipment`, `training`, `access`, `orientation` |
| `assigned_to_id` | `uuid` | FK â†’ users |
| `due_date` | `date` |  |
| `status` | `varchar(20)` | `pending`, `in_progress`, `completed` |
| `completed_at` | `timestamptz` |  |

**Foreign Keys:** `employee_id` â†’ [[#`employees`|employees]], `assigned_to_id` â†’ [[database/schemas/infrastructure#`users`|users]]

---

## `onboarding_templates`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` |  |
| `name` | `varchar(100)` |  |
| `department_id` | `uuid` | FK â†’ departments (nullable â€” global template) |
| `tasks_json` | `jsonb` | Template task definitions |

**Foreign Keys:** `department_id` â†’ [[database/schemas/org-structure#`departments`|departments]]

---

## Related

- [[modules/core-hr/overview|Core HR Module]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]


