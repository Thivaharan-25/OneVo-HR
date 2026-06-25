# Module: Org Structure

**Feature Folder:** `Application/Features/OrgStructure`
**Phase:** 1 - Build
**Pillar:** 1 - HR Management
**Owner:** Dev 3 (Week 1)
**Tables:** 7
**Task File:** [[current-focus/DEV3-org-structure|DEV3: Org Structure]]

---

## Purpose


Phase 1 supports both single-company and multi-company tenants. A single-company tenant has one Company. A multi-company tenant has multiple Companies under the same tenant. The user-facing operating context comes from the topbar-selected Company; internally, Company maps to `legal_entity_id` where the database still uses legal entity naming. Departments and positions are Company-specific.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[modules/infrastructure/overview\|Infrastructure]] | `ITenantContext` | Multi-tenancy |
| **Consumed by** | [[modules/core-hr/overview\|Core Hr]] | `IOrgStructureService` | Company, department, position, and position-derived reporting for employees |
| **Consumed by** | [[modules/time-off/overview\|Time Off]] | `IOrgStructureService` | Time Off policies by selected Company/country and employee assignment context |
| **Consumed by** | [[modules/payroll/overview\|Payroll]] | `IOrgStructureService` | Company context for payroll processing |
| **Consumed by** | [[modules/exception-engine/overview\|Exception Engine]] | `IOrgStructureService` | Department-scoped exception rules and position-resolved escalation context |

---

## Public Interface

```csharp
public interface IOrgStructureService
{
    Task<Result<List<LegalEntityDto>>> GetLegalEntitiesAsync(CancellationToken ct);
    Task<Result<DepartmentDto>> GetDepartmentAsync(Guid departmentId, CancellationToken ct);
    Task<Result<List<DepartmentDto>>> GetDepartmentHierarchyAsync(Guid legalEntityId, CancellationToken ct);
    Task<Result<ReportingTeamDto>> GetReportingTeamAsync(Guid managerEmployeeId, ReportingTeamDepth depth, CancellationToken ct);
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

## Key Database Tables

### `legal_entities`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `parent_legal_entity_id` | `uuid` | FK -> legal_entities, nullable |
| `name` | `varchar(200)` | |
| `display_name` | `varchar(200)` | Optional Company display name |
| `logo_file_id` | `uuid` | Nullable FK -> file_records |
| `registration_number` | `varchar(50)` | |
| `tax_identifier` | `varchar(80)` | nullable |
| `country_id` | `uuid` | FK -> countries |
| `currency_code` | `varchar(3)` | ISO 4217 currency for this Company |
| `address_json` | `jsonb` | |
| `timezone` | `varchar(50)` | IANA timezone for this Company |
| `default_language` | `varchar(10)` | |
| `date_format` | `varchar(20)` | |
| `week_start_day` | `smallint` | |
| `office_address_label` | `varchar(255)` | Company's single office location label |
| `office_latitude` | `decimal(10,7)` | Nullable until onsite verification is enabled |
| `office_longitude` | `decimal(10,7)` | Nullable until onsite verification is enabled |
| `office_allowed_radius_meters` | `int` | Required for onsite verification |
| `is_active` | `boolean` | |
| `created_at` | `timestamptz` | |

**Company General rule:** Settings > General edits the selected Company's general fields and single office location directly on `legal_entities`. Phase 1 has no separate office-location table and no office-location CRUD screen. If a customer needs another branch/sub-office, create another Company/legal entity.

### `departments`

Legal-entity-scoped department hierarchy via `parent_department_id`.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `legal_entity_id` | `uuid` | FK -> legal_entities |
| `name` | `varchar(100)` | Unique within selected Company |
| `code` | `varchar(20)` | Stable short identifier; unique within selected Company |
| `parent_department_id` | `uuid` | Self-referencing FK (nullable) |
| `head_position_id` | `uuid` | FK -> positions; must be `unique` type; nullable |
| `is_active` | `boolean` | |
| `created_at` | `timestamptz` | |

**Handle recursive queries with CTEs.**

Department names are used in customer-facing setup and import screens. Department codes remain internal/stable references for integrations and audit; normal employee CSV imports should not require HR admins to provide codes.

### `positions`

First-class org seats used to define reporting hierarchy. Positions are Company-scoped. Internally this maps to `legal_entity_id`. A position can report only to a `unique` position in the same Company so manager resolution is unambiguous.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `legal_entity_id` | `uuid` | FK -> legal_entities |
| `code` | `varchar(40)` | Stable tenant-unique identifier |
| `position_type` | `varchar(20)` | `unique` or `pooled` |
| `max_occupancy` | `int` | `1` for unique positions |
| `department_id` | `uuid` | FK -> departments |
| `reports_to_position_id` | `uuid` | Current reporting snapshot; FK -> same-legal-entity unique position, nullable for root positions |
| `is_active` | `boolean` | |


Rules: `unique` positions can be reporting targets and have one active occupant. `pooled` positions can have multiple occupants and cannot be reporting targets. Position hierarchy must reject cycles. `reports_to_position_id` is the current reporting snapshot; historical reporting changes are stored in `position_reporting_history`. A position cannot report to a position in another Company.

Internal position access grant rules generate `user_roles` grants or `access_grant_requests` when an employee is assigned, transferred, promoted, or onboarded into the position. Tenant-admin UX calls this **Grant system access from this position** and shows Role granted, Can manage employees in, and Requires approval. Phase 1 approval uses lightweight access requests and Notifications, not Workflow Engine.

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
Additional Authority Assignments may grant role/access/approval authority without changing time_off, schedule, attendance, payroll, holiday calendar, or primary Company. One employee cannot hold two active employment assignments inside the same Company.

### `employee_hierarchy_closure`

Current derived reporting tree used for fast reporting-team queries. It is rebuilt from `positions`, current `position_reporting_history`, and current `position_assignments`; users and workflows must not edit it directly. Historical reporting uses `position_assignments` plus `position_reporting_history`.

| Column | Type | Notes |
|:-------|:-----|:------|
| `tenant_id` | `uuid` | FK -> tenants |
| `ancestor_employee_id` | `uuid` | Resolved manager/ancestor employee |
| `descendant_employee_id` | `uuid` | Resolved subordinate employee |
| `depth` | `int` | `1` direct report, `2+` indirect report |
| `source_position_assignment_id` | `uuid` | Source assignment for the descendant |
| `generated_at` | `timestamptz` | Generation timestamp |

**Reporting team rule:** Phase 1 resolves manager reporting views from the reporting-manager structure. The reporting view for a manager is derived from `employee_hierarchy_closure`. Direct reports = `ancestor_employee_id = managerEmployeeId` and `depth = 1`; full reporting tree = `depth >= 1`. Reporting membership changes automatically when position assignments or reporting lines change.


## Domain Events (intra-module - MediatR)

> These events are published and consumed within this module only. They never cross the module boundary.

| Event | Published When | Handler |
|:------|:---------------|:--------|
| _(none)_ | - | - |

## Cross-Module Events (cross-module - MediatR INotification)

### Publishes

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `DepartmentChanged` | Department created, updated, or restructured | Downstream modules that index department context |
| `PositionCreated` | New position persisted | Core HR (position context cache) |
| `PositionUpdated` | Position name, max occupancy, or reporting target changed | Core HR, Exception Engine (escalation context) |
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
| POST | `/api/v1/org/legal-entities` | `org:manage` | Create Company |
| GET | `/api/v1/org/departments?view=tree\|flat` | `employees:read` | List departments for the selected Company |
| POST | `/api/v1/org/departments` | `org:manage` | Create department in selected Company |
| PUT | `/api/v1/org/departments/{id}` | `org:manage` | Update department in selected Company |
| GET | `/api/v1/org/positions` | `employees:read` | List positions for the selected Company |
| GET | `/api/v1/org/positions/tree` | `employees:read` | Position reporting tree for selected Company with occupancy and vacancy status |
| GET | `/api/v1/org/reporting-team?managerEmployeeId={id}&depth={direct|full}` | `employees:read` | Reporting-manager team derived from position hierarchy |
| POST | `/api/v1/org/positions` | `org:manage` | Create position |
| POST | `/api/v1/org/positions/bulk` | `org:manage` | Bulk create positions; returns per-item results |
| PUT | `/api/v1/org/positions/{id}` | `org:manage` | Update position name, max occupancy, reports-to |
| DELETE | `/api/v1/org/positions/{id}` | `org:manage` | Deactivate position (blocked if occupied) |
| POST | `/api/v1/employees/{id}/position-assignment` | `employees:write` | Assign employee to a position (owned by Core HR) |

## Features

- [[modules/org-structure/legal-entities/overview|Legal Entities]] - Single-company and multi-company legal employer structure
- [[modules/org-structure/departments/overview|Departments]] - Hierarchical department tree (`parent_department_id`, CTE-friendly)
- [[modules/org-structure/positions/overview|Positions]] - Company-scoped positions with max occupancy, reporting-position validation, and position assignments -> [[modules/org-structure/positions/end-to-end-logic|Logic]] / [[modules/org-structure/positions/testing|Tests]]
- [[modules/org-structure/reporting-teams/overview|Reporting Teams]] - Reporting views derived from position reporting structure

---

## Related

- [[infrastructure/multi-tenancy|Multi Tenancy]] - All org structure data is tenant-scoped
- [[backend/shared-kernel|Shared Kernel]] - Foundation entity patterns
- [[database/migration-patterns|Migration Patterns]] - Self-referencing `parent_department_id` and `reports_to_position_id` hierarchies; derived employee hierarchy closure
- [[current-focus/DEV3-org-structure|DEV3: Org Structure]] - Implementation task file

See also: [[backend/module-catalog|Module Catalog]], [[modules/core-hr/overview|Core Hr]], [[modules/time-off/overview|Time Off]], [[modules/payroll/overview|Payroll]]


