# Module: Core HR

**Feature Folder:** `Application/Features/CoreHR`
**Phase:** 1 - Build
**Pillar:** 1 - HR Management
**Owner:** Dev 1 + Dev 2 (Week 2)
**Tables:** 15
**Task Files:** [[current-focus/DEV1-core-hr-profile|DEV1: Core HR Profile]], [[current-focus/DEV2-core-hr-lifecycle|DEV2: Core HR Lifecycle]]

---

## Purpose

The **central hub** of ONEVO. Manages employee profiles, lifecycle events (onboarding, offboarding, promotions, transfers), and the Phase 1 employee data model (dependents, addresses, work history, bank details). Core HR supports both single-company and multi-company tenants by storing each employee's primary legal entity and current legal-entity-scoped position assignment. Qualification tracking and compensation setup are Phase 2. Nearly every other module depends on Core HR for employee context.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[modules/infrastructure/overview\|Infrastructure]] | `ITenantContext`, `IUserService`, `IFileService` | Multi-tenancy, user linking, avatar uploads |
| **Consumed by** | [[modules/time-off/overview\|Time Off]] | `IEmployeeService` | Employee context for Time Off |
| **Consumed by** | [[modules/payroll/overview\|Payroll]] | `IEmployeeService` | Employee salary, bank details |
| **Consumed by** | [[database/performance\|Performance]] | `IEmployeeService` | Employee context for reviews |
| **Consumed by** | [[modules/activity-monitoring/overview\|Activity Monitoring]] | `IEmployeeService` | Employee/department context |
| **Consumed by** | [[modules/time-attendance/overview\|Time & Attendance]] | `IEmployeeService` | Employee context for presence |
| **Consumed by** | [[modules/exception-engine/overview\|Exception Engine]] | `IEmployeeService` | Employee/department context for Phase 2 escalation resolver inputs |
| **Consumed by** | [[modules/productivity-analytics/overview\|Productivity Analytics]] | `IEmployeeService` | Employee/department for reports |

---

## Public Interface

```csharp
public interface IEmployeeService
{
    Task<Result<EmployeeDto>> GetByIdAsync(Guid employeeId, CancellationToken ct);
    Task<Result<EmployeeDto>> GetByUserIdAsync(Guid userId, CancellationToken ct);
    Task<Result<PagedResult<EmployeeDto>>> GetAllAsync(PagedRequest request, CancellationToken ct);
    Task<Result<EmployeeDto>> CreateAsync(CreateEmployeeCommand command, CancellationToken ct);
    Task<Result<EmployeeDto>> UpdateAsync(Guid employeeId, UpdateEmployeeCommand command, CancellationToken ct);
    Task<Result<EmployeeDto?>> ResolveReportingManagerAsync(Guid employeeId, DateOnly effectiveDate, CancellationToken ct);
    Task<Result<List<EmployeeDto>>> GetDirectReportsAsync(Guid employeeId, CancellationToken ct);
    Task<Result<List<EmployeeDto>>> GetByDepartmentAsync(Guid departmentId, CancellationToken ct);
}
```

---

## Code Location (Clean Architecture)

Domain entities:
  ONEVO.Domain/Features/CoreHR/Entities/
  ONEVO.Domain/Features/CoreHR/Events/

Application (CQRS):
  ONEVO.Application/Features/CoreHR/Commands/
  ONEVO.Application/Features/CoreHR/Queries/
  ONEVO.Application/Features/CoreHR/DTOs/Requests/
  ONEVO.Application/Features/CoreHR/DTOs/Responses/
  ONEVO.Application/Features/CoreHR/Validators/
  ONEVO.Application/Features/CoreHR/EventHandlers/

Infrastructure:
  ONEVO.Infrastructure/Persistence/Configurations/CoreHR/

API endpoints:
  ONEVO.Api/Controllers/CoreHR/CoreHRController.cs

---

## Database Tables (15)

### `employees`

Central hub entity. Linked 1:1 to `users` via `user_id`.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `user_id` | `uuid` | FK -> users (1:1) |
| `employee_number` | `varchar(20)` | Unique per tenant |
| `first_name` | `varchar(100)` | |
| `last_name` | `varchar(100)` | |
| `email` | `varchar(255)` | Work email |
| `phone` | `varchar(20)` | |
| `date_of_birth` | `date` | PII - CONFIDENTIAL |
| `gender` | `varchar(10)` | |
| `nationality_id` | `uuid` | FK -> countries |
| `department_id` | `uuid` | FK -> departments, nullable |
| `legal_entity_id` | `uuid` | FK -> legal_entities |
| `employment_type` | `varchar(20)` | `full_time`, `part_time`, `contract`, `intern` |
| `employment_status` | `varchar(20)` | `onboarding`, `active`, `on_leave`, `offboarding`, `suspended`, `terminated`, `resigned` |
| `work_mode` | `varchar(10)` | `onsite`, `remote`, `hybrid` |
| `hire_date` | `date` | |
| `probation_end_date` | `date` | Nullable |
| `termination_date` | `date` | Nullable |
| `avatar_file_id` | `uuid` | FK -> file_records |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |
| `is_deleted` | `boolean` | Soft delete |

**Reporting hierarchy:** Employee records do not store manager references. Current reporting is resolved through active `position_assignments`, current `position_reporting_history`, and the derived `employee_hierarchy_closure` table. Historical reporting uses `position_assignments` plus `position_reporting_history`.

### `employee_assignment_history`

Effective-dated assignment snapshot for department and position changes. Reporting history is resolved from `position_assignments` and position hierarchy by date.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `department_id` | `uuid` | FK -> departments, nullable |
| `position_id` | `uuid` | FK -> positions, nullable |
| `effective_from` | `date` | Start date |
| `effective_to` | `date` | nullable; null means current open assignment |

### `employee_transfers`

Lightweight request record for employee position or assignment transfer. This is not a Workflow Engine instance. Approved transfers close/create `position_assignments` and `employee_assignment_history` rows on the effective date.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK -> tenants |
| `employee_id` | `uuid` | FK -> employees |
| `from_department_id` | `uuid` | nullable |
| `to_department_id` | `uuid` | nullable |
| `from_position_id` | `uuid` | nullable |
| `to_position_id` | `uuid` | nullable |
| `effective_date` | `date` | When approved transfer becomes active |
| `status` | `varchar(30)` | `Pending`, `Approved`, `Rejected`, `Cancelled`, `Applied` |
| `reason` | `varchar(500)` | Business reason |
| `requested_by_id` | `uuid` | FK -> users |
| `approved_by_id` | `uuid` | FK -> users, nullable |

### `employee_addresses`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `employee_id` | `uuid` | FK -> employees |
| `address_type` | `varchar(20)` | `permanent`, `current`, `emergency` |
| `address_json` | `jsonb` | Street, city, state, postal, country |
| `is_primary` | `boolean` | |

### `employee_dependents`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `employee_id` | `uuid` | FK -> employees |
| `name` | `varchar(100)` | |
| `relationship` | `varchar(20)` | `spouse`, `child`, `parent`, `other` |
| `date_of_birth` | `date` | |
| `is_emergency_contact` | `boolean` | |
| `phone` | `varchar(20)` | |

### `employee_qualifications` - Phase 2

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `employee_id` | `uuid` | FK -> employees |
| `qualification_type` | `varchar(20)` | `degree`, `certification`, `license` |
| `title` | `varchar(200)` | |
| `institution` | `varchar(200)` | |
| `year_obtained` | `int` | |
| `expiry_date` | `date` | Nullable |
| `document_file_id` | `uuid` | FK -> file_records |

### `employee_work_history`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `employee_id` | `uuid` | FK -> employees |
| `company_name` | `varchar(200)` | |
| `start_date` | `date` | |
| `end_date` | `date` | |
| `reason_for_leaving` | `varchar(255)` | |

### `employee_salary_history` - Phase 2

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `employee_id` | `uuid` | FK -> employees |
| `effective_date` | `date` | |
| `base_salary` | `decimal(15,2)` | |
| `currency_code` | `varchar(3)` | |
| `change_reason` | `varchar(100)` | `hire`, `promotion`, `annual_review`, `adjustment` |
| `approved_by_id` | `uuid` | FK -> users |

### `employee_bank_details`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `employee_id` | `uuid` | FK -> employees |
| `bank_name` | `varchar(100)` | |
| `branch_name` | `varchar(100)` | |
| `account_number_encrypted` | `bytea` | **Encrypted** via `IEncryptionService` (AES-256) |
| `routing_number` | `varchar(20)` | |
| `is_primary` | `boolean` | |

### `employee_lifecycle_events`

Audit trail for promotions, transfers, suspension, termination, and other employee lifecycle events. Salary-change events are Phase 2 with compensation setup.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `employee_id` | `uuid` | FK -> employees |
| `event_type` | `varchar(30)` | `hired`, `promoted`, `transferred`, `salary_change`, `suspended`, `terminated`, `resigned` |
| `event_date` | `date` | |
| `details_json` | `jsonb` | Event-specific data |
| `performed_by_id` | `uuid` | FK -> users |
| `created_at` | `timestamptz` | |

### `employee_checklist_tasks`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `employee_id` | `uuid` | FK -> employees |
| `template_id` | `uuid` | FK -> checklist_templates, nullable for manual task |
| `lifecycle_type` | `varchar(20)` | `onboarding` or `offboarding` |
| `task_title` | `varchar(200)` | |
| `owner_type` | `varchar(30)` | `employee`, `manager`, `hr`, `it`, `custom_user` |
| `sequence` | `int` | Nullable display/order value |
| `assigned_to_id` | `uuid` | FK -> users |
| `due_date` | `date` | |
| `status` | `varchar(20)` | `pending`, `in_progress`, `completed` |
| `completed_at` | `timestamptz` | |

### `checklist_templates`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `name` | `varchar(100)` | |
| `template_type` | `varchar(20)` | `onboarding` or `offboarding` |
| `department_id` | `uuid` | FK -> departments (nullable - global template) |
| `tasks_json` | `jsonb` | Task definitions: title, owner type, due rule, and sequence |
| `is_active` | `boolean` | |

### `offboarding_records`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `employee_id` | `uuid` | FK -> employees |
| `reason` | `varchar(30)` | `resignation`, `termination`, `retirement`, `contract_end` |
| `last_working_date` | `date` | |
| `knowledge_risk_level` | `varchar(10)` | `low`, `medium`, `high`, `critical` |
| `exit_interview_notes` | `text` | |
| `penalties_json` | `jsonb` | Outstanding loans, notice period, etc. |
| `status` | `varchar(20)` | `initiated`, `in_progress`, `completed` |
| `created_at` | `timestamptz` | |

### `employee_emergency_contacts`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `employee_id` | `uuid` | FK -> employees |
| `name` | `varchar(100)` | |
| `relationship` | `varchar(30)` | |
| `phone` | `varchar(20)` | |
| `email` | `varchar(255)` | |
| `is_primary` | `boolean` | |

### `employee_custom_fields`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `employee_id` | `uuid` | FK -> employees |
| `field_name` | `varchar(100)` | |
| `field_value` | `text` | |
| `field_type` | `varchar(20)` | `text`, `number`, `date`, `boolean`, `select` |

---

## Domain Events (intra-module - MediatR)

> These events are published and consumed within this module only. They never cross the module boundary.

| Event | Published When | Handler |
|:------|:---------------|:--------|
| _(none)_ | - | - |

## Cross-Module Events (cross-module - MediatR INotification)

### Publishes

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `EmployeeHired` | New employee added | [[modules/time-off/overview\|Time Off]] (calculate initial Time Off entitlements), [[modules/time-attendance/overview\|Time & Attendance]], [[modules/calendar/overview\|Calendar]], [[modules/performance/overview\|Performance]], [[modules/skills/overview\|Skills]], [[modules/documents/overview\|Documents]], [[modules/notifications/overview\|Notifications]] |
| `EmployeePromoted` | Promotion event | [[modules/notifications/overview\|Notifications]] |
| `EmployeeTransferred` | Employee assignment change | [[modules/notifications/overview\|Notifications]] |
| `SalaryChanged` | Salary change recorded | [[modules/payroll/overview\|Payroll]] |
| `EmployeeOffboarded` | Termination/resignation completed | [[modules/agent-gateway/overview\|Agent Gateway]] (revoke agent), [[modules/documents/overview\|Documents]], [[modules/notifications/overview\|Notifications]] |
| `OnboardingStepCompleted` | Individual onboarding task completed | [[modules/notifications/overview\|Notifications]] |

### Consumes

| Event | Source Module | Action Taken |
|:------|:-------------|:-------------|
| _(none)_ | - | - |

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/employees` | `employees:read` | List employees (paginated) |
| GET | `/api/v1/employees/{id}` | `employees:read` | Get employee detail |
| POST | `/api/v1/employees` | `employees:write` | Create employee |
| PUT | `/api/v1/employees/{id}` | `employees:write` | Update employee |
| DELETE | `/api/v1/employees/{id}` | `employees:delete` | Soft delete |
| GET | `/api/v1/employees/me` | `employees:read-own` | Get own profile |
| GET | `/api/v1/employees/{id}/lifecycle` | `employees:read` | Lifecycle events |
| POST | `/api/v1/employees/{id}/onboarding` | `employees:write` | Start onboarding |
| POST | `/api/v1/employees/{id}/offboarding` | `employees:write` | Start offboarding |
| GET | `/api/v1/employees/{id}/salary-history` | `payroll:read` | Phase 2 salary history |
| PUT | `/api/v1/employees/{id}/bank-details` | `employees:write` | Update bank details (encrypted) |

## Features

- [[modules/core-hr/employee-profiles/overview|Employee Profiles]] - Central employee entity, addresses, custom fields - frontend: [[modules/core-hr/employee-profiles/frontend|Frontend]]
- [[modules/core-hr/employee-lifecycle/overview|Employee Lifecycle]] - Promotions, transfers, suspensions, terminations, salary changes
- [[modules/core-hr/onboarding/overview|Onboarding]] - Onboarding checklist tasks generated from Checklist Templates
- [[modules/core-hr/offboarding/overview|Offboarding]] - Offboarding records, exit interviews, penalty tracking
- [[modules/core-hr/dependents-contacts/overview|Dependents Contacts]] - Dependents and emergency contacts
- [[modules/core-hr/qualifications/overview|Qualifications]] - Phase 2; degrees, certifications, licenses with document upload
- [[modules/core-hr/compensation/overview|Compensation]] - Phase 2; salary history and compensation setup. Bank details remain in Phase 1 employee profile data.

---

## Related

- [[infrastructure/multi-tenancy|Multi Tenancy]] - Every employee and sub-entity is tenant-scoped
- [[security/data-classification|Data Classification]] - `date_of_birth` is PII-CONFIDENTIAL; `account_number_encrypted` is AES-256
- [[security/compliance|Compliance]] - Salary history and lifecycle events form immutable audit trail
- [[backend/messaging/event-catalog|Event Catalog]] - `EmployeeCreated`, `EmployeePromoted`, `EmployeeTransferred`, `EmployeeTerminated`
- [[backend/shared-kernel|Shared Kernel]] - `BaseEntity`, `BaseRepository` foundation
- [[database/migration-patterns|Migration Patterns]] - Soft-delete pattern (`is_deleted`), position-derived reporting hierarchy
- [[current-focus/DEV1-core-hr-profile|DEV1: Core HR Profile]] - Profile implementation task file
- [[current-focus/DEV2-core-hr-lifecycle|DEV2: Core HR Lifecycle]] - Lifecycle implementation task file

See also: [[backend/module-catalog|Module Catalog]], [[modules/infrastructure/overview|Infrastructure]], [[modules/org-structure/overview|Org Structure]], [[modules/time-off/overview|Time Off]], [[modules/payroll/overview|Payroll]]

