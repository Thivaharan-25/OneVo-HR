# Module: Org Structure

**Namespace:** `ONEVO.Modules.OrgStructure`
**Phase:** 1 — Build
**Pillar:** 1 — HR Management
**Owner:** Dev 3 (Week 1)
**Tables:** 8
**Task File:** [[current-focus/DEV3-org-structure|DEV3: Org Structure]]

---

## Purpose

Manages the organizational hierarchy: legal entities, departments (hierarchical with parent-child), job families/levels/titles, and teams. All HR modules reference Org Structure for department and job context.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[modules/infrastructure/overview\|Infrastructure]] | `ITenantContext` | Multi-tenancy |
| **Consumed by** | [[modules/core-hr/overview\|Core Hr]] | `IOrgStructureService` | Department, job context for employees |
| **Consumed by** | [[modules/leave/overview\|Leave]] | `IOrgStructureService` | Leave policies per job level/country |
| **Consumed by** | [[modules/payroll/overview\|Payroll]] | `IOrgStructureService` | Legal entity for payroll processing |
| **Consumed by** | [[modules/exception-engine/overview\|Exception Engine]] | `IOrgStructureService` | Department-scoped exception rules |

---

## Public Interface

```csharp
public interface IOrgStructureService
{
    Task<Result<DepartmentDto>> GetDepartmentAsync(Guid departmentId, CancellationToken ct);
    Task<Result<List<DepartmentDto>>> GetDepartmentHierarchyAsync(CancellationToken ct);
    Task<Result<LegalEntityDto>> GetLegalEntityAsync(Guid legalEntityId, CancellationToken ct);
    Task<Result<List<JobTitleDto>>> GetJobTitlesAsync(Guid? jobFamilyId, CancellationToken ct);
    Task<Result<List<TeamDto>>> GetTeamsByDepartmentAsync(Guid departmentId, CancellationToken ct);
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
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(200)` | |
| `registration_number` | `varchar(50)` | |
| `country_id` | `uuid` | FK → countries |
| `address_json` | `jsonb` | |
| `is_active` | `boolean` | |
| `created_at` | `timestamptz` | |

### `departments`

Self-referencing hierarchy via `parent_department_id`.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(100)` | |
| `code` | `varchar(20)` | |
| `parent_department_id` | `uuid` | Self-referencing FK (nullable) |
| `head_employee_id` | `uuid` | FK → employees (nullable) |
| `legal_entity_id` | `uuid` | FK → legal_entities |
| `is_active` | `boolean` | |
| `created_at` | `timestamptz` | |

**Handle recursive queries with CTEs.**

### `job_families`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(100)` | e.g., "Engineering", "Sales" |
| `description` | `varchar(500)` | |
| `created_at` | `timestamptz` | |

### `job_levels`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(50)` | e.g., "Junior", "Senior", "Lead", "Director" |
| `rank` | `int` | Numeric ordering |
| `created_at` | `timestamptz` | |

### `job_titles`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(100)` | e.g., "Software Engineer" |
| `job_family_id` | `uuid` | FK → job_families |
| `job_level_id` | `uuid` | FK → job_levels |
| `is_active` | `boolean` | |
| `created_at` | `timestamptz` | |

### `teams`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `name` | `varchar(100)` | |
| `department_id` | `uuid` | FK → departments |
| `team_lead_id` | `uuid` | FK → employees (nullable) |
| `is_active` | `boolean` | |
| `created_at` | `timestamptz` | |

### `team_members`

| Column | Type | Notes |
|:-------|:-----|:------|
| `team_id` | `uuid` | FK → teams |
| `employee_id` | `uuid` | FK → employees |
| `joined_at` | `timestamptz` | |
| PK: `(team_id, employee_id)` | | |

### `department_cost_centers`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `department_id` | `uuid` | FK → departments |
| `cost_center_code` | `varchar(20)` | |
| `budget_amount` | `decimal(15,2)` | |
| `fiscal_year` | `int` | |

### `hierarchy_scope_exceptions`

Cross-feature bypass grants that expand `IHierarchyScope` results for a specific employee.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `granted_to_employee_id` | `uuid` | FK → employees — who receives the bypass |
| `scope_type` | `varchar(20)` | `department` \| `people` \| `role` |
| `scope_id` | `uuid` | FK → departments / employees / roles depending on `scope_type` — always required |
| `applies_to` | `varchar(50)` | nullable — `null` = all features (root admin only); e.g. `'calendar'`, `'teams'` |
| `granted_by_employee_id` | `uuid` | FK → employees — audit trail |
| `created_at` | `timestamptz` | |
| `expires_at` | `timestamptz` | nullable |

Resolved by `IHierarchyScope.GetSubordinateIdsAsync()` — bypass targets are appended to `bypassIds` in the result. See [[modules/auth/authorization/end-to-end-logic|Authorization — Hierarchy Scoping]].

### `permission_delegation_scopes`

Records the module whitelist for employees who were granted `roles:manage` via delegation (not as base role).

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `delegated_to_employee_id` | `uuid` | FK → employees |
| `module_scope` | `text[]` | Modules this person can manage permissions and bypass grants for |
| `delegated_by_employee_id` | `uuid` | FK → employees — audit trail |
| `created_at` | `timestamptz` | |
| `expires_at` | `timestamptz` | nullable |

**Ceiling rule:** `module_scope` must be a strict subset of the granter's own `module_scope`. Employees with `roles:manage` from their base role (no `permission_delegation_scopes` record) are treated as root admins with unrestricted scope.

---

## Domain Events (intra-module — MediatR)

> These events are published and consumed within this module only. They never leave the module.

| Event | Published When | Handler |
|:------|:---------------|:--------|
| _(none)_ | — | — |

## Integration Events (cross-module — RabbitMQ)

### Publishes

| Event | Routing Key | Published When | Consumers |
|:------|:-----------|:---------------|:----------|
| `DepartmentChanged` | `org.department.changed` | Department created, updated, or restructured | Downstream modules that index department context |

### Consumes

| Event | Routing Key | Source Module | Action Taken |
|:------|:-----------|:-------------|:-------------|
| `TenantCreated` | `infrastructure.tenant.created` | [[modules/infrastructure/overview\|Infrastructure]] | Seed default department structure for new tenant |

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/departments` | `employees:read` | List departments (flat or tree) |
| POST | `/api/v1/departments` | `settings:admin` | Create department |
| PUT | `/api/v1/departments/{id}` | `settings:admin` | Update department |
| GET | `/api/v1/legal-entities` | `settings:admin` | List legal entities |
| POST | `/api/v1/legal-entities` | `settings:admin` | Create legal entity |
| GET | `/api/v1/job-families` | `employees:read` | List job families |
| GET | `/api/v1/job-titles` | `employees:read` | List job titles |
| GET | `/api/v1/teams` | `employees:read` | List teams |
| POST | `/api/v1/teams` | `settings:admin` | Create team |

## Features

- [[modules/org-structure/legal-entities/overview|Legal Entities]] — Legal entity registration with country and address
- [[modules/org-structure/departments/overview|Departments]] — Hierarchical department tree (`parent_department_id`, CTE-friendly)
- [[modules/org-structure/job-hierarchy/overview|Job Hierarchy]] — Job families, job levels (with rank), and job titles
- [[modules/org-structure/teams/overview|Teams]] — Teams within departments with team leads and member assignments
- [[modules/org-structure/cost-centers/overview|Cost Centers]] — Department cost centers with budget per fiscal year

---

## Related

- [[infrastructure/multi-tenancy|Multi Tenancy]] — All org structure data is tenant-scoped
- [[backend/shared-kernel|Shared Kernel]] — Foundation entity patterns
- [[database/migration-patterns|Migration Patterns]] — Self-referencing `parent_department_id` hierarchy; CTE queries
- [[current-focus/DEV3-org-structure|DEV3: Org Structure]] — Implementation task file

See also: [[backend/module-catalog|Module Catalog]], [[modules/core-hr/overview|Core Hr]], [[modules/leave/overview|Leave]], [[modules/payroll/overview|Payroll]]
