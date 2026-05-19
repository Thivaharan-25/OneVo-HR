# Org Structure — Schema

**Module:** [[modules/org-structure/overview|Org Structure]]
**Phase:** Phase 1
**Tables:** 9

---

## `office_locations`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(100)` | e.g., "Kuala Lumpur HQ — Floor 12" |
| `address_json` | `jsonb` | Street, city, state, postcode, country |
| `timezone` | `varchar(50)` | IANA timezone, e.g., `Asia/Kuala_Lumpur` |
| `is_active` | `boolean` |  |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `department_cost_centers`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `department_id` | `uuid` | FK → departments |
| `cost_center_code` | `varchar(20)` |  |
| `budget_amount` | `decimal(15,2)` |  |
| `fiscal_year` | `int` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `department_id` → [[#`departments`|departments]]

---

## `departments`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(100)` |  |
| `code` | `varchar(20)` |  |
| `parent_department_id` | `uuid` | Self-referencing FK (nullable) |
| `head_employee_id` | `uuid` | FK → employees (nullable) |
| `is_active` | `boolean` |  |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `head_employee_id` → [[database/schemas/core-hr#`employees`|employees]]

---

## `job_families`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(100)` | e.g., "Engineering", "Sales" |
| `description` | `varchar(500)` |  |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `job_levels`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `job_family_id` | `uuid` | FK → job_families |
| `name` | `varchar(50)` | e.g., "Junior", "Senior", "Lead", "Director" |
| `rank` | `int` | Numeric ordering — unique per job family |
| `salary_minimum` | `decimal(14,2)` | Nullable — indicative band minimum in tenant currency |
| `salary_maximum` | `decimal(14,2)` | Nullable — indicative band maximum in tenant currency |
| `default_role_id` | `uuid` | Nullable FK → roles — resolved when the linked role template is applied to this tenant |
| `pending_role_template_id` | `uuid` | Nullable FK → role_templates — set when a job family template references a role template that has not yet been applied; cleared and `default_role_id` is set when the role template is later applied |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `job_family_id` → [[#`job_families`|job_families]], `default_role_id` → [[database/schemas/auth#`roles`|roles]], `pending_role_template_id` → [[database/schemas/auth#`role_templates`|role_templates]]

**Unique constraint:** `(job_family_id, rank)` — rank must be unique within a family.

**Deferred role-linking rule:** When a Job Family template is applied and a level references a `role_template_id`:
- If that role template has already been applied to this tenant (`roles.source_template_id = role_template_id`): `default_role_id` is set immediately, `pending_role_template_id` stays null.
- If the role template has not been applied yet: `pending_role_template_id` is set, `default_role_id` stays null.
- When the role template is later applied, the system scans all `job_levels` for this tenant where `pending_role_template_id` matches, sets `default_role_id`, and clears `pending_role_template_id`.
- Employees at a level with no `default_role_id` require manual role assignment.

---

## `job_titles`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(100)` | e.g., "Software Engineer" |
| `job_family_id` | `uuid` | FK → job_families |
| `job_level_id` | `uuid` | FK → job_levels |
| `is_active` | `boolean` |  |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `job_family_id` → [[#`job_families`|job_families]], `job_level_id` → [[#`job_levels`|job_levels]]

---

## `company_registration_profiles`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(200)` |  |
| `registration_number` | `varchar(50)` |  |
| `country_id` | `uuid` | FK → countries |
| `currency_code` | `varchar(3)` | ISO 4217 currency for this company profile; defaults from selected country but can be overridden by operator |
| `address_json` | `jsonb` |  |
| `is_active` | `boolean` |  |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `country_id` → [[database/schemas/infrastructure#`countries`|countries]]

---

## `team_members`

| Column | Type | Notes |
|:-------|:-----|:------|
| `team_id` | `uuid` | FK → teams |
| `employee_id` | `uuid` | FK → employees |
| `joined_at` | `timestamptz` |  |

**Foreign Keys:** `team_id` → [[#`teams`|teams]], `employee_id` → [[database/schemas/core-hr#`employees`|employees]]

---

## `teams`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(100)` |  |
| `department_id` | `uuid` | FK → departments |
| `team_lead_id` | `uuid` | FK → employees (nullable) |
| `is_active` | `boolean` |  |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `department_id` → [[#`departments`|departments]], `team_lead_id` → [[database/schemas/core-hr#`employees`|employees]]

---

## Related

- [[modules/org-structure/overview|Org Structure Module]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]
