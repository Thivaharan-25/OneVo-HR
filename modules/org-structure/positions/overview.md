# Positions

**Module:** Org Structure  
**Feature:** Positions  
**Phase:** 1

---

## Purpose

Positions are the first-class org seats that define the reporting hierarchy. Employees are placed into positions — not into departments or teams directly. Position hierarchy is the source of truth for reporting lines; employee records do not store a `manager_id` field.

Each position belongs to exactly one legal entity. Positions cannot be shared across legal entities. Job Title, Job Family, and Job Level are not required in Phase 1 position setup.

## Position Types

| Type | Occupancy | Can be reporting target |
|:-----|:----------|:------------------------|
| `unique` | One active occupant at a time | Yes |
| `pooled` | Multiple concurrent occupants | No |

Reporting targets must be `unique` positions. `pooled` positions (e.g. "Software Engineer – Sri Lanka") hold headcount but cannot be named as a manager position.

## Phase 1 Rules

- Positions belong to one legal entity; `legal_entity_id` is immutable after creation.
- Legal entity is selected as the active Org Structure context before creating a position. It is not an editable field inside the Create Position form.
- A position can report only to a `unique` position in the same legal entity.
- Root positions (no `reports_to_position_id`) are allowed — used for CEO, Country Head, etc.
- Cycles in reporting chains are rejected.
- `reports_to_position_id` is the current reporting snapshot. Historical reporting changes are stored in `position_reporting_history`.
- Capacity reductions below current active occupancy are rejected.
- Position-linked roles are confirmed by an admin at each employee assignment, transfer, or promotion — never auto-applied.
- Old position-linked access is removed on position change unless the admin explicitly keeps it as manual access.
- Location, cost center, job title, job family, and job level are not required for Phase 1 setup.

## Database Tables

### `positions`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `legal_entity_id` | `uuid` | FK → legal_entities; immutable after creation |
| `department_id` | `uuid` | FK → departments; must belong to same legal entity |
| `name` | `varchar` | Unique within legal entity |
| `position_type` | `varchar(20)` | `unique` or `pooled` |
| `max_occupancy` | `int` | Headcount ceiling; `1` for unique; ≥ 1 for pooled |
| `reports_to_position_id` | `uuid` | FK → positions (same legal entity, unique type); nullable for root positions |
| `suggested_role_id` | `uuid` | FK → roles; optional onboarding/promotion suggestion only — never auto-applied |
| `is_active` | `bool` | |

### `position_reporting_history`

Effective-dated history of reporting changes. The authoritative source for historical reporting queries.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `position_id` | `uuid` | FK → positions |
| `reports_to_position_id` | `uuid` | FK → positions; nullable for root |
| `effective_from` | `DateOnly` | |
| `effective_to` | `DateOnly` | Nullable; open-ended if null |

Rules: reporting targets must be `unique` positions; date ranges cannot overlap for the same position; cycles are rejected for the effective date range.

### `position_assignments`

Effective-dated employee placement into positions.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `employee_id` | `uuid` | FK → employees |
| `position_id` | `uuid` | FK → positions |
| `effective_from` | `DateOnly` | |
| `effective_to` | `DateOnly` | Nullable; open-ended if current |

Rules: one active primary assignment per employee in Phase 1. Unique positions may have only one active occupant at a time.

### `employee_hierarchy_closure`

Derived reporting tree rebuilt from current `positions`, `position_reporting_history`, and `position_assignments`. Used for fast scope queries. Never edited directly; rebuilt on reporting changes.

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/org/positions?legalEntityId={id}` | `employees:read` | List positions for a legal entity |
| GET | `/api/v1/org/positions/tree?legalEntityId={id}` | `employees:read` | Reporting tree with occupancy and vacancy status |
| POST | `/api/v1/org/positions` | `org:manage` | Create position |
| POST | `/api/v1/org/positions/bulk` | `org:manage` | Create multiple positions in one request; returns per-item results |
| PUT | `/api/v1/org/positions/{id}` | `org:manage` | Update position name, max occupancy, reports-to |
| DELETE | `/api/v1/org/positions/{id}` | `org:manage` | Deactivate position (blocked if occupied) |

Employee assignment (`POST /api/v1/employees/{id}/position-assignment`) is owned by Core HR, not this module. Org Structure exposes `IOrgStructureService` for position resolution.

## Service Interface (consumed by other modules)

```csharp
public interface IOrgStructureService
{
    Task<Result<List<PositionDto>>> GetPositionsAsync(Guid legalEntityId, CancellationToken ct);
    Task<Result<PositionDto>> GetPositionByIdAsync(Guid positionId, CancellationToken ct);
    Task<Result<PositionDto>> GetEmployeeCurrentPositionAsync(Guid employeeId, CancellationToken ct);
    Task<Result<List<PositionDto>>> GetReportingChainAsync(Guid positionId, CancellationToken ct);
}
```

Consumed by:
- **Core HR** — position context for employee records, transfer, promotion
- **Exception Engine** — position-resolved escalation context
- **Leave / Attendance** — manager resolution from reporting chain

## Related

- [[modules/org-structure/overview|Org Structure]]
- [[modules/org-structure/legal-entities/overview|Legal Entities]]
- [[modules/org-structure/departments/overview|Departments]]
- [[modules/org-structure/job-hierarchy/overview|Job Hierarchy]]
- [[modules/core-hr/overview|Core HR]]
- [[Userflow/Org-Structure/position-setup|Position Setup]]
- [[current-focus/DEV3-org-structure|DEV3: Org Structure]]
