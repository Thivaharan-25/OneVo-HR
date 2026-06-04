# Module: Org Structure

**Feature Folder:** `Application/Features/OrgStructure`
**Phase:** 1 â€” Build
**Pillar:** 1 â€” HR Management
**Owner:** Dev 3 (Week 1)
**Tables:** 16
**Task File:** [[current-focus/DEV3-org-structure|DEV3: Org Structure]]

---

## Purpose

Manages the organizational hierarchy: legal entities, departments, positions, position assignments, shared job titles, and teams. Position hierarchy is the source of truth for reporting; employee records do not store manager references.

Phase 1 supports both single-company and multi-company tenants. A single-company tenant has one legal entity. A multi-company tenant has multiple legal entities under the same tenant. Departments and positions are legal-entity-specific. Job titles are tenant-shared catalog values.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[modules/infrastructure/overview\|Infrastructure]] | `ITenantContext` | Multi-tenancy |
| **Consumed by** | [[modules/core-hr/overview\|Core Hr]] | `IOrgStructureService` | Legal entity, department, position, job context, and position-derived reporting for employees |
| **Consumed by** | [[modules/leave/overview\|Leave]] | `IOrgStructureService` | Leave policies by legal entity/country and employee assignment context |
| **Consumed by** | [[modules/payroll/overview\|Payroll]] | `IOrgStructureService` | Legal entity context for payroll processing |
| **Consumed by** | [[modules/exception-engine/overview\|Exception Engine]] | `IOrgStructureService` | Department-scoped exception rules and position-resolved escalation context |

---

## Public Interface

```csharp
public interface IOrgStructureService
{
    Task<Result<List<LegalEntityDto>>> GetLegalEntitiesAsync(CancellationToken ct);
    Task<Result<DepartmentDto>> GetDepartmentAsync(Guid departmentId, CancellationToken ct);
    Task<Result<List<DepartmentDto>>> GetDepartmentHierarchyAsync(Guid legalEntityId, CancellationToken ct);
    Task<Result<List<JobTitleDto>>> GetJobTitlesAsync(Guid? jobFamilyId, CancellationToken ct);
    Task<Result<List<TeamDto>>> GetTeamsAsync(CancellationToken ct);
    Task<Result<List<PositionDto>>> GetPositionsAsync(Guid legalEntityId, CancellationToken ct);
    Task<Result<PositionDto>> GetPositionByIdAsync(Guid positionId, CancellationToken ct);
    Task<Result<PositionDto>> GetEmployeeCurrentPositionAsync(Guid employeeId, CancellationToken ct);
    Task<Result<List<PositionDto>>> GetReportingChainAsync(Guid positionId, CancellationToken ct);
    Task<Result<EmployeeDto?>> ResolveReportingManagerAsync(Guid employeeId, DateOnly effectiveDate, CancellationToken ct);
    Task<Result<List<EmployeeDto>>> GetDirectReportsAsync(Guid employeeId, CancellationToken ct);
}
```

---

## Code Location (Clean Architecture)

Domain entities:
  ONEVO.Domain/Features/OrgStructure/Entities/
  ONEVO.Domain/Features/OrgStructure/Events/

Application (CQRS):
  ONEVO.Application/Features/OrgStructure/Commands/
  ONEVO.Application/Features/OrgStructure/Queries/
  ONEVO.Application/Features/OrgStructure/DTOs/Requests/
  ONEVO.Application/Features/OrgStructure/DTOs/Responses/
  ONEVO.Application/Features/OrgStructure/Validators/
  ONEVO.Application/Features/OrgStructure/EventHandlers/

Infrastructure:
  ONEVO.Infrastructure/Persistence/Configurations/OrgStructure/

API endpoints:
  ONEVO.Api/Controllers/OrgStructure/OrgStructureController.cs

---

## Database Tables (10)

### `legal_entities`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK â†’ tenants |
| `parent_legal_entity_id` | `uuid` | FK -> legal_entities, nullable |
| `name` | `varchar(200)` | |
| `registration_number` | `varchar(50)` | |
| `tax_identifier` | `varchar(80)` | nullable |
| `country_id` | `uuid` | FK â†’ countries |
| `currency_code` | `varchar(3)` | ISO 4217 currency for this legal entity |
| `address_json` | `jsonb` | |
| `is_active` | `boolean` | |
| `created_at` | `timestamptz` | |

### `office_locations`

Office and work-site locations used by HR, presence, identity verification, and configuration flows.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `name` | `varchar(100)` | e.g., "Colombo HQ - Floor 4" |
| `address_json` | `jsonb` | Street, city, state, postcode, country |
| `timezone` | `varchar(50)` | IANA timezone |
| `is_active` | `boolean` | |
| `created_at` | `timestamptz` | |

### `departments`

Legal-entity-scoped department hierarchy via `parent_department_id`.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK â†’ tenants |
| `legal_entity_id` | `uuid` | FK -> legal_entities |
| `name` | `varchar(100)` | Unique within legal entity |
| `code` | `varchar(20)` | Stable short identifier; unique within legal entity |
| `parent_department_id` | `uuid` | Self-referencing FK (nullable) |
| `head_position_id` | `uuid` | FK â†’ positions; must be `unique` type; nullable |
| `is_active` | `boolean` | |
| `created_at` | `timestamptz` | |

**Handle recursive queries with CTEs.**

Department names are used in customer-facing setup and import screens. Department codes remain internal/stable references for integrations and audit; normal employee CSV imports should not require HR admins to provide codes.

### `job_families`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK â†’ tenants |
| `name` | `varchar(100)` | e.g., "Engineering", "Sales" |
| `description` | `varchar(500)` | |
| `created_at` | `timestamptz` | |

### `job_levels`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK â†’ tenants |
| `job_family_id` | `uuid` | FK -> job_families |
| `name` | `varchar(50)` | e.g., "Junior", "Senior", "Lead", "Director" |
| `rank` | `int` | Numeric ordering, unique within job family |
| `suggested_role_id` | `uuid` | FK to roles (nullable) - optional onboarding/promotion suggestion only; never auto-assigned |
| `created_at` | `timestamptz` | |

Job levels describe career hierarchy and compensation bands. They must not directly grant security permissions, team authority, or WorkSync access. A job level may prefill a suggested role during onboarding or promotion, but an authorized admin must confirm the actual security role, team role, workspace membership, and project membership.

### `job_titles`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK â†’ tenants |
| `name` | `varchar(100)` | e.g., "Software Engineer" |
| `job_family_id` | `uuid` | FK → job_families; nullable — a title can exist without a family |
| `job_level_id` | `uuid` | FK → job_levels; nullable — a title can exist without a level |
| `is_active` | `boolean` | |
| `created_at` | `timestamptz` | |


### `positions`

First-class org seats used to define reporting hierarchy. Positions are legal-entity-scoped. A position can report only to a `unique` position in the same legal entity so manager resolution is unambiguous.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `legal_entity_id` | `uuid` | FK -> legal_entities |
| `code` | `varchar(40)` | Stable tenant-unique identifier |
| `name` | `varchar(120)` | e.g., "Team Lead - Backend", "Software Engineer" |
| `position_type` | `varchar(20)` | `unique` or `pooled` |
| `max_occupancy` | `int` | `1` for unique positions |
| `department_id` | `uuid` | FK -> departments |
| `job_title_id` | `uuid` | FK -> job_titles |
| `reports_to_position_id` | `uuid` | Current reporting snapshot; FK -> same-legal-entity unique position, nullable for root positions |
| `is_active` | `boolean` | |

Minimal Phase 1 setup fields are position name, legal entity, department, job title, capacity, reports-to position, and linked roles/permissions. Location, cost center, job family, and job level are not required for Phase 1 position setup.

Rules: `unique` positions can be reporting targets and have one active occupant. `pooled` positions can have multiple occupants and cannot be reporting targets. Position hierarchy must reject cycles. `reports_to_position_id` is the current reporting snapshot; historical reporting changes are stored in `position_reporting_history`. A position cannot report to a position in another legal entity.

Position-linked roles/permissions are confirmed when an employee is assigned, transferred, or promoted into the position. Old position-linked access is removed on position change unless the admin confirms it should remain as manual access.

### `position_reporting_history`

Effective-dated reporting relationship history between positions. This table is the historical source of truth for position reporting changes.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `position_id` | `uuid` | FK -> positions |
| `reports_to_position_id` | `uuid` | FK -> positions, nullable for root positions |
| `effective_from` | `date` | Start date |
| `effective_to` | `date` | nullable; null means current reporting relationship |
| `created_at` | `timestamptz` | |

Rules: reporting targets must be `unique` positions, effective date ranges cannot overlap for the same position, and reporting changes must reject cycles for the effective date range.

### `position_assignments`

Effective-dated employee placement into positions.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `position_id` | `uuid` | FK -> positions |
| `effective_from` | `date` | Start date |
| `effective_to` | `date` | nullable; null means current assignment |
| `assignment_status` | `varchar(20)` | `active`, `planned`, `ended`, `cancelled` |

Rules: one active primary position assignment per employee in Phase 1. Unique positions can have only one active occupant.

### `employee_hierarchy_closure`

Current derived reporting tree used for fast scope queries. It is rebuilt from `positions`, current `position_reporting_history`, and current `position_assignments`; users and workflows must not edit it directly. Historical reporting uses `position_assignments` plus `position_reporting_history`.

| Column | Type | Notes |
|:-------|:-----|:------|
| `tenant_id` | `uuid` | FK -> tenants |
| `ancestor_employee_id` | `uuid` | Resolved manager/ancestor employee |
| `descendant_employee_id` | `uuid` | Resolved subordinate employee |
| `depth` | `int` | `1` direct report, `2+` indirect report |
| `source_position_assignment_id` | `uuid` | Source assignment for the descendant |
| `generated_at` | `timestamptz` | Generation timestamp |

### `teams`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK â†’ tenants |
| `name` | `varchar(100)` | Unique within tenant |
| `description` | `text` | nullable |
| `is_active` | `boolean` | |
| `created_at` | `timestamptz` | |


Teams do not own or require a department. Department reporting is derived from `team_members -> employees.department_id`. Team lead/admin behavior is derived from `team_member_roles -> team_roles -> team_role_permissions`; do not store `team_lead_id`.
### `team_members`

| Column | Type | Notes |
|:-------|:-----|:------|
| `team_id` | `uuid` | FK â†’ teams |
| `employee_id` | `uuid` | FK â†’ employees |
| `joined_at` | `timestamptz` | |
| `left_at` | `timestamptz` | nullable; null means active membership |
| PK: `(team_id, employee_id)` | | |

### `team_roles`

Tenant-defined team role permission sets for scoped authority inside an HR team. They are configured in Roles & Permissions under Team Roles and assigned to employees only through team membership.

Allowed standard names:

- Admin / Lead
- Member
- Viewer / Reviewer

Team roles are not tenant security roles. They must not be used for HR Admin, Project Admin, Payroll Admin, System Admin, Tenant Owner, or other module/system authority.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK to tenants |
| `name` | `varchar(80)` | `Admin / Lead`, `Member`, or `Viewer / Reviewer` |
| `description` | `text` | nullable |
| `is_system` | `boolean` | Seeded roles cannot be deleted |
| `created_at` | `timestamptz` | |

### `team_member_roles`

Assigns a team role to an employee inside one team.

| Column | Type | Notes |
|:-------|:-----|:------|
| `team_id` | `uuid` | FK to teams |
| `employee_id` | `uuid` | FK to employees |
| `team_role_id` | `uuid` | FK to team_roles |
| `effective_from` | `timestamptz` | |
| `effective_to` | `timestamptz` | nullable |
| PK: `(team_id, employee_id, team_role_id)` | | |

### `team_role_permissions`

Maps team roles to scoped work-context permissions.

| Column | Type | Notes |
|:-------|:-----|:------|
| `team_role_id` | `uuid` | FK to team_roles |
| `permission_id` | `uuid` | FK to permissions |
| PK: `(team_role_id, permission_id)` | | |

Team role permissions can support WorkSync actions when the HR team is linked to a workspace. They must stay scoped to the linked team/work area and must not grant tenant-wide HR, payroll, security, billing, project visibility, or system administration authority. Project visibility still requires `project_members`.

### `department_cost_centers` â€” Phase 2

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK â†’ tenants |
| `department_id` | `uuid` | FK â†’ departments |
| `cost_center_code` | `varchar(20)` | |
| `budget_amount` | `decimal(15,2)` | |
| `fiscal_year` | `int` | |

## Domain Events (intra-module â€” MediatR)

> These events are published and consumed within this module only. They never leave the module.

| Event | Published When | Handler |
|:------|:---------------|:--------|
| _(none)_ | â€” | â€” |

## Cross-Module Events (cross-module â€” MediatR INotification)

### Publishes

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `DepartmentChanged` | Department created, updated, or restructured | Downstream modules that index department context |
| `PositionCreated` | New position persisted | Core HR (position context cache) |
| `PositionUpdated` | Position name, capacity, or reporting target changed | Core HR, Exception Engine (escalation context) |
| `PositionDeactivated` | Position set inactive | Core HR (guard against new assignments) |

### Consumes

| Event | Source Module | Action Taken |
|:------|:-------------|:-------------|
| `TenantCreated` | [[modules/infrastructure/overview\|Infrastructure]] | Seed default department structure for new tenant |

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/org/legal-entities` | `org:read` | List legal entities |
| POST | `/api/v1/org/legal-entities` | `org:manage` | Create legal entity |
| GET | `/api/v1/org/departments?legalEntityId={id}` | `employees:read` | List departments for a legal entity (flat or tree) |
| POST | `/api/v1/org/departments` | `org:manage` | Create department |
| PUT | `/api/v1/org/departments/{id}` | `org:manage` | Update department |
| GET | `/api/v1/org/positions?legalEntityId={id}` | `employees:read` | List positions for a legal entity |
| GET | `/api/v1/org/positions/tree?legalEntityId={id}` | `employees:read` | Position reporting tree with occupancy and vacancy status |
| POST | `/api/v1/org/positions` | `org:manage` | Create position |
| POST | `/api/v1/org/positions/bulk` | `org:manage` | Bulk create positions; returns per-item results |
| PUT | `/api/v1/org/positions/{id}` | `org:manage` | Update position name, capacity, job title, reports-to |
| DELETE | `/api/v1/org/positions/{id}` | `org:manage` | Deactivate position (blocked if occupied) |
| POST | `/api/v1/employees/{id}/position-assignment` | `employees:write` | Assign employee to a position (owned by Core HR) |
| GET | `/api/v1/org/job-titles` | `employees:read` | List job titles |
| POST | `/api/v1/org/job-titles` | `org:manage` | Create job title; `job_family_id` and `job_level_id` are optional |
| PUT | `/api/v1/org/job-titles/{id}` | `org:manage` | Update job title, or link/unlink family and level |
| GET | `/api/v1/org/job-families` | `employees:read` | List job families |
| GET | `/api/v1/org/job-levels?familyId={id}` | `employees:read` | List job levels for a job family |
| POST | `/api/v1/org/job-levels` | `org:manage` | Create job level within a job family |
| PUT | `/api/v1/org/job-levels/{id}` | `org:manage` | Update job level name or rank |
| GET | `/api/v1/org/teams` | `employees:read` | List teams |
| POST | `/api/v1/org/teams` | `org:manage` | Create team and assign team roles only |
| PUT | `/api/v1/org/teams/{id}/members/{employeeId}/roles` | `org:manage` | Replace this member's team roles; accepts `team_roles` only |

## Features

- [[modules/org-structure/legal-entities/overview|Legal Entities]] â€” Single-company and multi-company legal employer structure
- [[modules/org-structure/departments/overview|Departments]] â€” Hierarchical department tree (`parent_department_id`, CTE-friendly)
- [[modules/org-structure/job-hierarchy/overview|Job Hierarchy]] — Job titles (required for positions; `job_family_id` and `job_level_id` nullable), job families, and job levels with numeric rank and optional suggested role
- [[modules/org-structure/positions/overview|Positions]] — Legal-entity-scoped positions with capacity, reporting-position validation, and position assignments → [[modules/org-structure/positions/end-to-end-logic|Logic]] · [[modules/org-structure/positions/testing|Tests]]
- [[modules/org-structure/teams/overview|Teams]] - Tenant-scoped employee groups with leadership derived from team role assignments
- [[modules/org-structure/cost-centers/overview|Cost Centers]] â€” Phase 2; department cost centers with budget per fiscal year

---

## Related

- [[infrastructure/multi-tenancy|Multi Tenancy]] â€” All org structure data is tenant-scoped
- [[backend/shared-kernel|Shared Kernel]] â€” Foundation entity patterns
- [[database/migration-patterns|Migration Patterns]] â€” Self-referencing `parent_department_id` and `reports_to_position_id` hierarchies; derived employee hierarchy closure
- [[current-focus/DEV3-org-structure|DEV3: Org Structure]] â€” Implementation task file

See also: [[backend/module-catalog|Module Catalog]], [[modules/core-hr/overview|Core Hr]], [[modules/leave/overview|Leave]], [[modules/payroll/overview|Payroll]]


