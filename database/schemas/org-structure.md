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

**Phase 1 setup fields:** Position Name, active Legal Entity Context, Department, Position Type, Capacity / Max Occupancy, Reports To Position, and optional Position Access Templates. Legal entity is selected as the Org Structure working context before creation and is not an editable Create Position field. Job title, job family, and job level catalogs are not part of the Phase 1 org model.

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

## `position_access_templates`

Position-defined access templates used to generate scoped `user_roles` grants or access approval requests when an employee is onboarded, assigned, transferred, or promoted into a position. The template itself is not an active permission grant.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `position_id` | `uuid` | FK -> positions |
| `role_id` | `uuid` | FK -> roles |
| `scope_type` | `varchar(30)` | `Organization`, `Department`, `DepartmentTree`, `Team`, `Own`, `DirectReports`, or `ReportingTree` |
| `scope_id` | `uuid` | Nullable. Department/team id when scope needs a boundary; null for `Organization`, `Own`, `DirectReports`, and `ReportingTree` |
| `requires_approval` | `boolean` | True for sensitive or broad grants that must be confirmed by access authority |
| `is_sensitive` | `boolean` | Marks templates that expose sensitive HR, payroll, security, or broad employee data |
| `effective_from_rule` | `varchar(30)` | `assignment_effective_from` or explicit date rule |
| `effective_to_rule` | `varchar(30)` | Nullable. Usually `assignment_effective_to` |
| `is_active` | `boolean` | Inactive templates are ignored for future assignments |
| `created_by` | `uuid` | FK -> users |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` | nullable |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `position_id` -> [[#`positions`|positions]], `role_id` -> [[database/schemas/auth#`roles`|roles]], `created_by` -> [[database/schemas/infrastructure#`users`|users]]

**Rules:**
- Creating or editing templates requires `roles:manage` or `access:approve`.
- For HR positions, `scope_id` is the coverage department, not necessarily `positions.department_id`.
- If `requires_approval = true` and the employee movement actor lacks `roles:manage` or `access:approve`, the backend creates an `access_grant_requests` record instead of activating the grant.
- Approval routing uses the target position's department.
- Pooled position template edits affect all current and future occupants unless the authorized user chooses an employee-specific grant/override during assignment.

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


