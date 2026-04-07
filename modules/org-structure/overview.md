# Module: Org Structure

**Namespace:** `ONEVO.Modules.OrgStructure`
**Pillar:** 1 — HR Management
**Owner:** Dev 3 (Week 1)
**Tables:** 8
**Task File:** [[WEEK1-org-structure]]

---

## Purpose

Manages the organizational hierarchy: legal entities, departments (hierarchical with parent-child), job families/levels/titles, and teams. All HR modules reference Org Structure for department and job context.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[infrastructure]] | `ITenantContext` | Multi-tenancy |
| **Consumed by** | [[core-hr]] | `IOrgStructureService` | Department, job context for employees |
| **Consumed by** | [[leave]] | `IOrgStructureService` | Leave policies per job level/country |
| **Consumed by** | [[payroll]] | `IOrgStructureService` | Legal entity for payroll processing |
| **Consumed by** | [[exception-engine]] | `IOrgStructureService` | Department-scoped exception rules |

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

## Database Tables (8)

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

- [[legal-entities]] — Legal entity registration with country and address
- [[departments]] — Hierarchical department tree (`parent_department_id`, CTE-friendly)
- [[job-hierarchy]] — Job families, job levels (with rank), and job titles
- [[teams]] — Teams within departments with team leads and member assignments
- [[cost-centers]] — Department cost centers with budget per fiscal year

---

## Related

- [[multi-tenancy]] — All org structure data is tenant-scoped
- [[shared-kernel]] — Foundation entity patterns
- [[migration-patterns]] — Self-referencing `parent_department_id` hierarchy; CTE queries
- [[WEEK1-org-structure]] — Implementation task file

See also: [[module-catalog]], [[core-hr]], [[leave]], [[payroll]]
