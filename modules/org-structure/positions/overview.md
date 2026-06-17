# Positions

**Module:** Org Structure  
**Feature:** Positions  
**Phase:** 1

---

## Purpose

Positions are first-class org seats that define the reporting hierarchy. Employees are placed into positions, not into departments or teams directly. Position hierarchy is the source of truth for reporting lines; employee records do not store a `manager_id` field.

Each position belongs to exactly one legal entity. Positions cannot be shared across legal entities. Job title, job family, and job level catalogs are not part of the Phase 1 position model.

## Position Types

| Type | Occupancy | Can be reporting target |
|:-----|:----------|:------------------------|
| `unique` | One active occupant at a time | Yes |
| `pooled` | Multiple concurrent occupants | No |

Reporting targets must be `unique` positions. `pooled` positions hold headcount but cannot be named as a manager position.

## Phase 1 Rules

- Positions belong to one legal entity; `legal_entity_id` is immutable after creation.
- Legal entity is selected as the active Org Structure context before creating a position. It is not an editable field inside the Create Position form.
- A position can report only to a `unique` position in the same legal entity.
- Root positions with no `reports_to_position_id` are allowed.
- Cycles in reporting chains are rejected.
- `reports_to_position_id` is the current reporting snapshot. Historical reporting changes are stored in `position_reporting_history`.
- Capacity reductions below current active occupancy are rejected.
- Position access templates generate scoped `user_roles` grants or access approval requests during onboarding, assignment, transfer, or promotion. The position template itself is never an active grant.
- Sensitive templates may require approval. If the movement actor lacks `roles:manage` or `access:approve`, generated sensitive access remains pending and routes by target position department.
- Old grants sourced from the previous position end on position change unless an authorized access user explicitly keeps equivalent access as manual access.
- For pooled positions, access-template edits affect all current and future occupants unless the authorized user chooses an employee-specific grant/override during assignment.
- Location, cost center, job title, job family, and job level catalogs are not part of Phase 1 setup.

## Database Tables

### `positions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `legal_entity_id` | `uuid` | FK -> legal_entities; immutable after creation |
| `department_id` | `uuid` | FK -> departments; must belong to same legal entity |
| `name` | `varchar` | Unique within legal entity |
| `position_type` | `varchar(20)` | `unique` or `pooled` |
| `max_occupancy` | `int` | Headcount ceiling; `1` for unique; >= 1 for pooled |
| `reports_to_position_id` | `uuid` | FK -> positions (same legal entity, unique type); nullable for root positions |
| `is_active` | `bool` | |

### `position_access_templates`

Optional templates that define generated access for employees assigned to a position. Templates are evaluated during onboarding, assignment, transfer, and promotion. The generated `user_roles` row or `access_grant_requests` row is the actual security artifact.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `position_id` | `uuid` | FK -> positions |
| `role_id` | `uuid` | FK -> roles |
| `scope_type` | `varchar(30)` | `Organization`, `Department`, `DepartmentTree`, `Own`, `DirectReports`, or `ReportingTree` |
| `scope_id` | `uuid` | Nullable; department id when the scope needs a department boundary |
| `requires_approval` | `boolean` | True for sensitive/broad access |
| `is_sensitive` | `boolean` | Marks HR, payroll, security, or broad employee-data access |
| `is_active` | `boolean` | Inactive templates are ignored |

### `position_reporting_history`

Effective-dated history of reporting changes. The authoritative source for historical reporting queries.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `position_id` | `uuid` | FK -> positions |
| `reports_to_position_id` | `uuid` | FK -> positions; nullable for root positions |
| `effective_from` | `date` | Start date |
| `effective_to` | `date` | Nullable |

### `position_assignments`

Effective-dated employee placement into positions.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `position_id` | `uuid` | FK -> positions |
| `effective_from` | `date` | Start date |
| `effective_to` | `date` | Nullable |
| `assignment_status` | `varchar(20)` | `active`, `planned`, `ended`, `cancelled` |

## Related Flows

- [[Userflow/Org-Structure/position-setup|Position Setup]]
- [[Userflow/Employee-Management/employee-onboarding|Employee Onboarding]]
- [[Userflow/Employee-Management/employee-transfer|Employee Transfer]]
- [[Userflow/Employee-Management/employee-promotion|Employee Promotion]]
- [[Userflow/Auth-Access/access-policy|Access Policy Reference]]
