# Org Structure - Schema

**Module:** [[modules/org-structure/overview|Org Structure]]
**Phase:** Phase 1
**Tables:** 7

---

## `legal_entities`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `parent_legal_entity_id` | `uuid` | FK -> legal_entities, nullable |
| `name` | `varchar(200)` | Legal company/entity name |
| `display_name` | `varchar(200)` | Optional customer-facing Company display name |
| `logo_file_id` | `uuid` | Nullable FK -> file_records |
| `registration_number` | `varchar(50)` | nullable |
| `tax_identifier` | `varchar(80)` | nullable |
| `country_id` | `uuid` | FK -> countries |
| `currency_code` | `varchar(3)` | ISO 4217 currency |
| `address_json` | `jsonb` |  |
| `timezone` | `varchar(50)` | IANA timezone for the Company. Primary timezone for schedule time interpretation, attendance reconciliation, late rules, overtime, and Time Off hour/day conversion. Schedule holiday country does not override this value |
| `default_language` | `varchar(10)` | e.g., `en` |
| `date_format` | `varchar(20)` | Company display preference |
| `week_start_day` | `smallint` | 1-7, implementation-defined mapping |
| `office_address_label` | `varchar(255)` | Display label for the Company's single office location |
| `office_latitude` | `decimal(10,7)` | Nullable until onsite verification is enabled |
| `office_longitude` | `decimal(10,7)` | Nullable until onsite verification is enabled |
| `office_allowed_radius_meters` | `int` | Required when onsite work-location verification is enabled |
| `is_active` | `boolean` |  |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `country_id` -> [[database/schemas/infrastructure#`countries`|countries]], `parent_legal_entity_id` -> [[#`legal_entities`|legal_entities]], `logo_file_id` -> [[database/schemas/infrastructure#`file_records`|file_records]]

**Rules:**
- A single-company tenant has one legal entity.
- A multi-company tenant can have multiple legal entities inside the same tenant.
- Departments, positions, employees, Time Off policy assignments, payroll setup, and legal-entity-scoped calendars resolve through `legal_entity_id`.
- User-facing term is Company; internal storage term is `legal_entities`.
- Settings > General edits the selected Company's general fields on this table.
- Each Company has one office location, stored directly on `legal_entities` through `office_*` columns.
- If a customer needs another branch, sub-office, or physical office, create another Company/legal entity. Phase 1 has no office-location CRUD table.

---

## `departments`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `legal_entity_id` | `uuid` | FK -> legal_entities |
| `name` | `varchar(100)` | Unique within legal entity |
| `code` | `varchar(20)` | Stable short identifier; unique within legal entity |
| `parent_department_id` | `uuid` | Self-referencing FK (nullable) |
| `head_position_id` | `uuid` | FK -> positions; must be `unique` type; nullable |
| `is_active` | `boolean` |  |
| `created_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `legal_entity_id` -> [[#`legal_entities`|legal_entities]], `head_position_id` -> [[#`positions`|positions]]

**Circular FK note:** `departments.head_position_id -> positions` and `positions.department_id -> departments` are mutually nullable. Create the department first with `head_position_id = NULL`, create the position with `department_id` set, then update the department. Application must also enforce that the head position belongs to the same legal entity and is `unique` type.

**Code rule:** Department names are shown in normal setup and employee CSV imports. Department codes are stable internal references for integrations, reports, payroll exports, and audit. Renaming a department should not change `code` unless an authorized admin performs an explicit code change.

---

## `positions`

First-class org seats used to define reporting hierarchy. Positions are legal-entity-scoped. Position hierarchy is the source of truth for reporting; employees do not store a manager reference.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `legal_entity_id` | `uuid` | FK -> legal_entities |
| `name` | `varchar(100)` | Position name; unique within legal entity |
| `code` | `varchar(40)` | Stable tenant-unique identifier for import and integrations |
| `position_type` | `varchar(20)` | `unique` or `pooled` |
| `max_occupancy` | `int` | Must be `1` for `unique`; greater than or equal to `1` for `pooled` |
| `department_id` | `uuid` | FK -> departments |
| `reports_to_position_id` | `uuid` | Current reporting snapshot; self-referencing FK to a same-legal-entity `unique` position, nullable for root positions |
| `is_active` | `boolean` |  |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` | nullable |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `legal_entity_id` -> [[#`legal_entities`|legal_entities]], `department_id` -> [[#`departments`|departments]], `reports_to_position_id` -> [[#`positions`|positions]]

**Phase 1 setup fields:** Position Name, Legal Entity Context, Department, Position Type, Capacity / Max Occupancy, Reports To Position, Status, and optional access block enabled by "Grant system access from this position".

**Position reporting rules:**
- `unique` positions must have `max_occupancy = 1`.
- Only `unique` positions can be selected as `reports_to_position_id`.
- `pooled` positions can have multiple occupants and cannot be used as reporting targets.
- A position cannot report to itself.
- A position cannot report to a position in another legal entity.
- Position hierarchy updates must reject circular reporting chains.
- Inactive positions cannot be selected as reporting targets.
- `reports_to_position_id` is the current reporting snapshot only. Historical reporting changes are stored in `position_reporting_history`.
- `reports_to_position_id` builds the org chart and automatically creates locked position-level management coverage for the reporting position. The generated coverage is source `ReportingStructure`, `is_locked = true`, and can be removed only by changing the child position's Reports to value.

---

## `position_access_templates`

Internal persistence for the role/access grant part of **Grant system access from this position**. Tenant-admin UX must call this **Grant system access from this position**, not "Position Access Templates". These rules generate deterministic `user_roles` grants or `access_grant_requests` records when an employee is onboarded, assigned, transferred, or promoted into a position. The rule itself is not an active permission grant. Employee visibility and approval routing are not stored here; they are resolved from `management_coverage_records`.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `position_id` | `uuid` | FK -> positions |
| `role_id` | `uuid` | FK -> roles |
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
- Creating or editing position access templates requires `roles:manage`. Approving generated position access requires `position:approve` with valid management coverage.
- `role_id` is the deterministic **Role granted** from the position.
- **Can manage employees in** is stored in `management_coverage_records`, not on the position access template.
- If `requires_approval = true` or the employee movement actor lacks authority, the backend creates an `access_grant_requests` record instead of activating the grant.
- Phase 1 approval routing uses management coverage through Notifications. It does not invoke Workflow Engine.
- Pooled position access-rule edits affect all current and future occupants.

---

## `management_coverage_records`

Single source for employee visibility and Phase 1 approval routing. `Reports to` automatically creates locked position-level coverage. Manual coverage is added from **Grant system access from this position**.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `legal_entity_id` | `uuid` | FK -> legal_entities; selected Company context |
| `owner_position_id` | `uuid` | FK -> positions; position that can manage the covered target |
| `covered_target_type` | `varchar(20)` | `Position`, `Department`, or `Company` |
| `covered_position_id` | `uuid` | Nullable FK -> positions; required when target type is `Position` |
| `covered_department_id` | `uuid` | Nullable FK -> departments; required when target type is `Department` |
| `owner_order` | `int` | Internal ordering only: 1 = Primary owner, 2 = Backup owner 1, 3 = Backup owner 2 |
| `source` | `varchar(30)` | `ReportingStructure` or `Manual` |
| `is_locked` | `boolean` | True for generated reporting-structure coverage |
| `status` | `varchar(20)` | `active` or `inactive` |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` |  |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `legal_entity_id` -> [[#`legal_entities`|legal_entities]], `owner_position_id` -> [[#`positions`|positions]], `covered_position_id` -> [[#`positions`|positions]], `covered_department_id` -> [[#`departments`|departments]]

**Rules:**
- Coverage levels are only Position, Department, and Company. There is no employee-specific coverage.
- `source = ReportingStructure` rows are generated from `positions.reports_to_position_id`, have `is_locked = true`, and cannot be removed manually.
- `source = Manual` rows have `is_locked = false` and can be added or removed by authorized admins.
- The first active owner for a covered target is Primary owner. Later owners are Backup owner 1, Backup owner 2, and so on. Primary owner / Backup owner labels are display labels for ordered management coverage owners. They are not hardcoded routing slots. Backend routing must support any number of active coverage owners.
- For monitoring alerts, recipient selection is availability-based through Monitoring Policy. For approval routing, owners are ordered by `owner_order` and permission checks; if the first owner is unavailable and the workflow/policy requires availability-aware routing, continue to the next eligible owner.
- The UI must not expose numeric priority, fallback checkboxes, or owner order fields.
- **Make primary** reorders owners for the same target, keeps locked generated coverage present, and shifts existing owners down.
- When Reports to changes, remove old generated locked coverage for the old reporting relation, create new locked coverage for the new relation, preserve manual coverage, and recompute owner order for affected targets.

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
| `assignment_kind` | `varchar(30)` | `PrimaryEmployment` or `AdditionalAuthority` |
| `effective_from` | `date` | Start date for this assignment |
| `effective_to` | `date` | Nullable. Null means current open assignment |
| `assignment_status` | `varchar(20)` | `active`, `planned`, `ended`, `cancelled` |
| `created_at` | `timestamptz` |  |
| `updated_at` | `timestamptz` | nullable |

**Foreign Keys:** `tenant_id` -> [[database/schemas/infrastructure#`tenants`|tenants]], `employee_id` -> [[database/schemas/core-hr#`employees`|employees]], `position_id` -> [[#`positions`|positions]]

**Assignment rules:**
- An employee must have exactly one active `PrimaryEmployment` assignment.
- The primary assignment is the only source for primary legal entity, Time Off policy, attendance/clock-in policy, work schedule, holiday calendar, and payroll/statutory employment context.
- Additional `AdditionalAuthority` assignments may grant role/access/approval authority and operational visibility.
- Additional authority assignments do not create a second Time Off policy, schedule, attendance policy, payroll context, holiday calendar, or primary legal entity.
- One employee cannot hold two active employment assignments inside the same legal entity. Use transfer or promotion instead.
- Cross-legal-entity authority assignments are allowed.
- Cross-legal-entity reporting lines are not allowed.
- A `unique` position can have only one active occupant.
- A `pooled` position can have at most `max_occupancy` active occupants.
- Closing or creating a current primary assignment triggers hierarchy closure rebuild for the affected branch.

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

**Reporting team rule:** A manager's reporting view is derived from this table. For direct reports, query rows where `ancestor_employee_id = manager_employee_id` and `depth = 1`. For the full reporting tree, use `depth >= 1`. Reporting membership changes when position assignments or reporting lines change.

---


## Related

- [[modules/org-structure/overview|Org Structure Module]]
- [[database/schema-catalog|Schema Catalog]]
- [[database/migration-patterns|Migration Patterns]]
- [[database/performance|Performance]]
