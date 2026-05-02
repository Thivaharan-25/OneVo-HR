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
| `legal_entity_id` | `uuid` | FK → legal_entities |
| `name` | `varchar(100)` | e.g., "Kuala Lumpur HQ — Floor 12" |
| `address_json` | `jsonb` | Street, city, state, postcode, country |
| `timezone` | `varchar(50)` | IANA timezone, e.g., `Asia/Kuala_Lumpur` |
| `is_active` | `boolean` |  |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `legal_entity_id` → [[#`legal_entities`|legal_entities]]

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
| `legal_entity_id` | `uuid` | FK → legal_entities |
| `is_active` | `boolean` |  |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]], `head_employee_id` → [[database/schemas/core-hr#`employees`|employees]], `legal_entity_id` → [[#`legal_entities`|legal_entities]]

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
| `name` | `varchar(50)` | e.g., "Junior", "Senior", "Lead", "Director" |
| `rank` | `int` | Numeric ordering |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` → [[database/schemas/infrastructure#`tenants`|tenants]]

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

## `legal_entities`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(200)` |  |
| `registration_number` | `varchar(50)` |  |
| `country_id` | `uuid` | FK → countries |
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