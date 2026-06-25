# Positions

**Module:** Org Structure  
**Feature:** Positions  
**Phase:** 1

---

## Purpose

Positions are first-class org seats. They define reporting hierarchy, Company-scoped structure, occupancy, optional default access, and management coverage. Internally, the selected Company maps to `legal_entity_id`.

Employees are assigned to positions. Employee records do not store `manager_id`; reporting is derived from active primary position assignments and the position reporting chain.

---

## Phase 1 Rules

- Positions belong to one Company; internal `legal_entity_id` is immutable after creation.
- Departments belong to one Company.
- A position can report only to a `unique` position in the same Company.
- Root positions with no `reports_to_position_id` are allowed.
- Cycles in reporting chains are rejected.
- Capacity reductions below current active occupancy are rejected.
- Org chart is for visualization; permission editing opens the position modal/detail.
- Optional system access is hidden until the admin enables **Grant system access from this position**.
- Role granted from position is deterministic.
- `Reports to` automatically creates locked position-level management coverage for the reporting position.
- Management coverage is the single source for employee visibility and Phase 1 approval routing.
- Phase 1 does not use Workflow Engine for position access approval.

---

## Position Types

| Type | Occupancy | Can be reporting target |
|:-----|:----------|:------------------------|
| `unique` | One active occupant at a time | Yes |
| `pooled` | Multiple concurrent occupants up to capacity | No |

---

## Position Create/Edit UX

### Core Position Structure

| Field | Notes |
|:---|:---|
| Position name | Required |
| Position code | Optional |
| Company context | Required; comes from topbar-selected Company |
| Department | Required; filtered by selected Company |
| Reports to | Required unless root position; same Company only |
| Type | Unique or pooled |
| Capacity / max occupancy | Required |
| Status | Active/inactive |
| Description / notes | Optional |

### Optional Access Block

Shown only after **Grant system access from this position**.

| Field | Notes |
|:---|:---|
| Role granted | Default granted role from this position |
| Can manage employees in | Selected positions, selected departments, or entire company |
| Requires approval | Access remains pending until the management coverage resolver assigns one eligible owner |

The UI uses Primary owner, Backup owner 1, Backup owner 2, System access from reporting structure, and Make primary. It must not expose numeric owner order, fallback checkboxes, or internal scope language.

> Primary owner / Backup owner labels are display labels for ordered management coverage owners. They are not hardcoded routing slots. Backend routing must support any number of active coverage owners. For monitoring alerts, recipient selection is availability-based through Monitoring Policy. For approval routing, owners are ordered by `owner_order` and permission checks; if the first owner is unavailable and the workflow/policy requires availability-aware routing, continue to the next eligible owner.

---

## Database Tables

### `positions`

Key fields: `tenant_id`, `legal_entity_id`, `department_id`, `name`, `code`, `position_type`, `max_occupancy`, `reports_to_position_id`, `is_active`.

### `position_access_templates`

Internal persistence for the position access grant rule. The tenant-admin UI must not call this "Position Access Templates"; it is the data behind **Grant system access from this position**.

Key fields: `position_id`, `role_id`, `requires_approval`, `is_sensitive`, `is_active`.

Generated `user_roles` rows are the actual active grants. If approval is required, an `access_grant_requests` record is created and approvers are notified.

### `management_coverage_records`

Single source for employee visibility and Phase 1 approval routing.

Key fields: `legal_entity_id`, `owner_position_id`, `covered_target_type`, `covered_position_id`, `covered_department_id`, `owner_order`, `source`, `is_locked`, `status`.

Rules:

- Coverage levels are Position, Department, and Company only.
- `Reports to` creates locked `ReportingStructure` coverage.
- Manual coverage comes from **Grant system access from this position**.
- More specific coverage wins: Position, then Department, then Company-wide.
- Within a target, Primary owner is tried first, then Backup owner 1, Backup owner 2, and so on.
- If no valid owner exists for approval routing, create a routing issue instead of assigning randomly or sending duplicates.

### `position_reporting_history`

Effective-dated history of reporting changes.

### `position_assignments`

Effective-dated employee placement into positions.

Assignment kinds:

- `PrimaryEmployment`
- `AdditionalAuthority`

The primary assignment is the only source for primary Company, Time Off policy, attendance policy, work schedule, holiday calendar, and payroll/statutory employment context.

Additional authority assignments may grant role/access/approval authority but do not change employment policy inheritance.

---

## Position List

Columns: Position, Department, Reports to, Occupant, Role granted, Manages employees in, Access status, Actions.

Access summary example:

- Role: HR Manager
- Manages: Engineering
- Approval: Required

---

## Related Flows

- [[Userflow/Org-Structure/position-setup|Position Setup]]
- [[Userflow/Employee-Management/employee-onboarding|Employee Onboarding]]
- [[Userflow/Employee-Management/employee-transfer|Employee Transfer]]
- [[Userflow/Employee-Management/employee-promotion|Employee Promotion]]
- [[Userflow/Auth-Access/access-policy|Management Coverage Reference]]
