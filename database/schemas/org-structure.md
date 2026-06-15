# Org Structure â€” Schema

**Module:** [[modules/org-structure/overview|Org Structure]]
**Phase:** Phase 1
**Tables:** 16

---

## `office_locations`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK â†’ tenants |
| `name` | `varchar(100)` | e.g., "Kuala Lumpur HQ â€” Floor 12" |
| `address_json` | `jsonb` | Street, city, state, postcode, country |
| `timezone` | `varchar(50)` | IANA timezone, e.g., `Asia/Kuala_Lumpur` |
| `is_active` | `boolean` |  |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` â†’ [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `department_cost_centers`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK â†’ tenants |
| `department_id` | `uuid` | FK â†’ departments |
| `cost_center_code` | `varchar(20)` |  |
| `budget_amount` | `decimal(15,2)` |  |
| `fiscal_year` | `int` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `department_id` -> [[#`departments`|departments]]

---

## `legal_entities`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `parent_legal_entity_id` | `uuid` | FK -> legal_entities, nullable |
| `name` | `varchar(200)` | Legal company/entity name |
| `registration_number` | `varchar(50)` | nullable |
| `tax_identifier` | `varchar(80)` | nullable |
| `country_id` | `uuid` | FK -> countries |
| `currency_code` | `varchar(3)` | ISO 4217 currency |
| `address_json` | `jsonb` |  |
| `is_active` | `boolean` |  |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `country_id` -> [[database/schemas/infrastructure#`countries`|countries]], `parent_legal_entity_id` -> [[#`legal_entities`|legal_entities]]

**Rules:**
- A single-company tenant has one legal entity.
- A multi-company tenant can have multiple legal entities inside the same tenant.
- Departments, positions, employees, leave policy assignments, payroll setup, and legal-entity-scoped calendars resolve through `legal_entity_id`.

---

## `departments`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK â†’ tenants |
| `legal_entity_id` | `uuid` | FK -> legal_entities |
| `name` | `varchar(100)` | Unique within legal entity |
| `code` | `varchar(20)` | Stable short identifier; unique within legal entity |
| `parent_department_id` | `uuid` | Self-referencing FK (nullable) |
| `head_position_id` | `uuid` | FK â†’ positions; must be `unique` type; nullable |
| `is_active` | `boolean` |  |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` â†’ [[database/schemas/infrastructure#`tenants`|tenants]], `legal_entity_id` -> [[#`legal_entities`|legal_entities]], `head_position_id` â†’ [[#`positions`|positions]]

**Circular FK note:** `departments.head_position_id → positions` and `positions.department_id → departments` are mutually nullable. Create the department first with `head_position_id = NULL`, create the position with `department_id` set, then update the department. Application must also enforce that the head position belongs to the same legal entity and is `unique` type.

**Code rule:** Department names are shown in normal setup and employee CSV imports. Department codes are stable internal references for integrations, reports, payroll exports, and audit. Renaming a department should not change `code` unless an authorized admin performs an explicit code change.

---

## `job_families`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK â†’ tenants |
| `name` | `varchar(100)` | e.g., "Engineering", "Sales" |
| `description` | `varchar(500)` |  |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` â†’ [[database/schemas/infrastructure#`tenants`|tenants]]

---

## `job_levels`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK â†’ tenants |
| `job_family_id` | `uuid` | FK â†’ job_families |
| `name` | `varchar(50)` | e.g., "Junior", "Senior", "Lead", "Director" |
| `rank` | `int` | Numeric ordering â€” unique per job family |
| `salary_minimum` | `decimal(14,2)` | Nullable â€” indicative band minimum in tenant currency |
| `salary_maximum` | `decimal(14,2)` | Nullable â€” indicative band maximum in tenant currency |
| `suggested_role_id` | `uuid` | Nullable FK to roles - suggested assignment only; never auto-assigned to employees |
| `pending_role_template_id` | `uuid` | Nullable FK to role_templates - pending suggested role template; cleared and `suggested_role_id` is set when the template is later applied |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` â†’ [[database/schemas/infrastructure#`tenants`|tenants]], `job_family_id` â†’ [[#`job_families`|job_families]], `suggested_role_id` â†’ [[database/schemas/auth#`roles`|roles]], `pending_role_template_id` â†’ [[database/schemas/auth#`role_templates`|role_templates]]

**Unique constraint:** `(job_family_id, rank)` â€” rank must be unique within a family.

**Suggested role prefill rule:** When a Job Family template is applied and a level references a `role_template_id`:
- If that role template has already been applied to this tenant (`roles.source_template_id = role_template_id`): `suggested_role_id` is set immediately, `pending_role_template_id` stays null.
- If the role template has not been applied yet: `pending_role_template_id` is set, `suggested_role_id` stays null.
- When the role template is later applied, the system scans all `job_levels` for this tenant where `pending_role_template_id` matches, sets `suggested_role_id`, and clears `pending_role_template_id`.
- `suggested_role_id` only pre-fills onboarding, promotion, or transfer screens. It must not auto-assign security roles, team roles, workspace membership, or project membership.
- Employees at a level with no `suggested_role_id` require manual role selection when a role is needed.

---

## `job_titles`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK â†’ tenants |
| `name` | `varchar(100)` | e.g., "Software Engineer" |
| `job_family_id` | `uuid` | FK â†’ job_families |
| `job_level_id` | `uuid` | FK â†’ job_levels |
| `is_active` | `boolean` |  |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` â†’ [[database/schemas/infrastructure#`tenants`|tenants]], `job_family_id` â†’ [[#`job_families`|job_families]], `job_level_id` â†’ [[#`job_levels`|job_levels]]

---

## `positions`

First-class org seats used to define reporting hierarchy. Positions are legal-entity-scoped. Position hierarchy is the source of truth for reporting; employees do not store a manager reference.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `legal_entity_id` | `uuid` | FK -> legal_entities |
| `code` | `varchar(40)` | Stable tenant-unique identifier for import and integrations |
| `name` | `varchar(120)` | e.g., "Team Lead - Backend", "Software Engineer" |
| `position_type` | `varchar(20)` | `unique` or `pooled` |
| `max_occupancy` | `int` | Must be `1` for `unique`; greater than or equal to `1` for `pooled` |
| `department_id` | `uuid` | FK -> departments |
| `reports_to_position_id` | `uuid` | Current reporting snapshot; self-referencing FK to a same-legal-entity `unique` position, nullable for root positions |
| `is_active` | `boolean` |  |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` | nullable |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `legal_entity_id` -> [[#`legal_entities`|legal_entities]], `department_id` -> [[#`departments`|departments]], `reports_to_position_id` -> [[#`positions`|positions]]

**Phase 1 setup fields:** Position Name, active Legal Entity Context, Department, Position Type, Capacity / Max Occupancy, Reports To Position, Linked Roles/Permissions. Legal entity is selected as the Org Structure working context before creation and is not an editable Create Position field. Job Title, Job Family, Job Level, Location, and Cost Center are not required in Phase 1 position setup.

**Position reporting rules:**
- `unique` positions must have `max_occupancy = 1`.
- Only `unique` positions can be selected as `reports_to_position_id`.
- `pooled` positions can have multiple occupants and cannot be used as reporting targets.
- A position cannot report to itself.
- A position cannot report to a position in another legal entity.
- Position hierarchy updates must reject circular reporting chains.
- Inactive positions cannot be selected as reporting targets.
- `reports_to_position_id` is the current reporting snapshot only. Historical reporting changes are stored in `position_reporting_history`.

---

## `position_reporting_history`

Effective-dated reporting relationship history between positions. This is the historical source of truth for position reporting changes.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `position_id` | `uuid` | FK -> positions |
| `reports_to_position_id` | `uuid` | FK -> positions, nullable for root positions |
| `effective_from` | `date` | Start date for this reporting relationship |
| `effective_to` | `date` | Nullable. Null means current open reporting relationship |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `position_id` -> [[#`positions`|positions]], `reports_to_position_id` -> [[#`positions`|positions]]

**Reporting history rules:**
- `reports_to_position_id` must point to a `unique` position when present.
- `position_id` and `reports_to_position_id` must belong to the same legal entity when `reports_to_position_id` is present.
- A position cannot report to itself for any effective date range.
- A position cannot have overlapping reporting rows for the same effective date range.
- Position reporting changes must reject circular reporting chains for the effective date range.
- Root positions use `reports_to_position_id = null`.

---

## `position_assignments`

Effective-dated employee placement into positions. Manager resolution comes from the assigned position's reporting chain.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `position_id` | `uuid` | FK -> positions |
| `effective_from` | `date` | Start date for this assignment |
| `effective_to` | `date` | Nullable. Null means current open assignment |
| `assignment_status` | `varchar(20)` | `active`, `planned`, `ended`, `cancelled` |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` | nullable |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` -> [[database/schemas/core-hr#`employees`|employees]], `position_id` -> [[#`positions`|positions]]

**Assignment rules:**
- An employee can have only one active primary position assignment in Phase 1.
- A `unique` position can have only one active occupant.
- A `pooled` position can have at most `max_occupancy` active occupants.
- Closing or creating a current assignment triggers hierarchy closure rebuild for the affected branch.

---

## `employee_hierarchy_closure`

Current derived reporting tree for fast hierarchy queries. This table is not source of truth and must be rebuildable from `positions`, current `position_reporting_history`, and current `position_assignments`. Historical reporting uses `position_assignments` plus `position_reporting_history`.

| Column | Type | Notes |
|:-------|:-----|:------|
| `tenant_id` | `uuid` | FK -> tenants |
| `ancestor_employee_id` | `uuid` | Resolved manager/ancestor employee |
| `descendant_employee_id` | `uuid` | Resolved subordinate employee |
| `depth` | `int` | `1` for direct reports, greater than `1` for indirect reports |
| `source_position_assignment_id` | `uuid` | FK -> position_assignments that produced the descendant placement |
| `generated_at` | `timestamptz` | When this row was generated |

**Primary Key:** `(tenant_id, ancestor_employee_id, descendant_employee_id)`

**Rebuild triggers:** current position reporting changes, position assignment changes, employee offboarding, employee position transfer, position deactivation, and occupancy correction.

**Rule:** Users and business workflows must not edit this table directly. It stores current hierarchy only and is safe to delete and rebuild.

---

## `team_members`

| Column | Type | Notes |
|:-------|:-----|:------|
| `team_id` | `uuid` | FK â†’ teams |
| `employee_id` | `uuid` | FK â†’ employees |
| `joined_at` | `timestamptz` |  |
| `left_at` | `timestamptz` | Nullable. Null means active team membership |

**Foreign Keys:** `team_id` â†’ [[#`teams`|teams]], `employee_id` â†’ [[database/schemas/core-hr#`employees`|employees]]

**Active membership rule:** Current team membership is `left_at IS NULL`. Historical team membership remains available for reporting and audit.

**Reporting-team rule:** Do not store every reporting manager's hierarchy as `teams`/`team_members`. A reporting manager's "team" is a virtual reporting team resolved from `employee_hierarchy_closure`. Store `team_members` only for explicit reusable groups, cross-functional groups, reviewer pools, or teams the customer intentionally manages as named groups.

---

## `team_roles`

Standard team role permission sets. Configured from Roles & Permissions, assigned only through team membership.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `name` | `varchar(80)` | `Admin / Lead`, `Member`, or `Viewer / Reviewer` |
| `description` | `text` | nullable |
| `is_system` | `boolean` | true for standard seeded team roles |
| `created_at` | `timestamptz` |  |

**Rule:** Team roles are not security roles. They must not represent HR Admin, Project Admin, Payroll Admin, System Admin, Tenant Owner, or any other tenant/module authority.

---

## `team_member_roles`

Assigns a team role to an employee inside one team.

| Column | Type | Notes |
|:-------|:-----|:------|
| `team_id` | `uuid` | FK -> teams |
| `employee_id` | `uuid` | FK -> employees |
| `team_role_id` | `uuid` | FK -> team_roles |
| `effective_from` | `timestamptz` |  |
| `effective_to` | `timestamptz` | nullable |

**Primary Key:** `(team_id, employee_id, team_role_id)`

**Rule:** Team creation and team editing may write `team_member_roles`, but must accept only `team_roles`. They must not accept security `roles`.

---

## `team_role_permissions`

Maps team roles to scoped team/workspace permissions.

| Column | Type | Notes |
|:-------|:-----|:------|
| `team_role_id` | `uuid` | FK -> team_roles |
| `permission_id` | `uuid` | FK -> permissions |

**Primary Key:** `(team_role_id, permission_id)`

**Rule:** `team_role_permissions` may contain only team/workspace-scoped permissions. It must reject tenant security, HR admin, payroll, billing, project visibility, system settings, and security role management permissions.

---

## `teams`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK â†’ tenants |
| `name` | `varchar(100)` | Unique within tenant |
| `description` | `text` | nullable |
| `is_active` | `boolean` |  |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]]


**Leadership rule:** Team leadership is derived from `team_member_roles -> team_roles -> team_role_permissions`; `teams` must not store `team_lead_id`.

**Workspace source rule:** WorkSync can create a workspace from "My Reporting Team" by resolving hierarchy and writing `workspace_members`; that flow must not create a duplicate stored team.
---

## Related

- [[modules/org-structure/overview|Org Structure Module]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]


