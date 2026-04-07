# Module: Core HR

**Namespace:** `ONEVO.Modules.CoreHR`
**Pillar:** 1 — HR Management
**Owner:** Dev 1 + Dev 2 (Week 2)
**Tables:** 13
**Task Files:** [[WEEK2-core-hr-profile]], [[WEEK2-core-hr-lifecycle]]

---

## Purpose

The **central hub** of ONEVO. Manages employee profiles, lifecycle events (onboarding, offboarding, promotions, transfers), and the full employee data model (dependents, addresses, qualifications, work history, salary, bank details). Nearly every other module depends on Core HR for employee context.

---

## Dependencies

| Direction | Module | Interface | Purpose |
|:----------|:-------|:----------|:--------|
| **Depends on** | [[infrastructure]] | `ITenantContext`, `IUserService`, `IFileService` | Multi-tenancy, user linking, avatar uploads |
| **Depends on** | [[org-structure]] | `IOrgStructureService` | Department, job title, team context |
| **Consumed by** | [[leave]] | `IEmployeeService` | Employee context for leave |
| **Consumed by** | [[payroll]] | `IEmployeeService` | Employee salary, bank details |
| **Consumed by** | [[performance]] | `IEmployeeService` | Employee context for reviews |
| **Consumed by** | [[activity-monitoring]] | `IEmployeeService` | Employee/department context |
| **Consumed by** | [[workforce-presence]] | `IEmployeeService` | Employee context for presence |
| **Consumed by** | [[exception-engine]] | `IEmployeeService` | Manager hierarchy for escalation |
| **Consumed by** | [[productivity-analytics]] | `IEmployeeService` | Employee/department for reports |

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
    Task<Result<Guid>> GetManagerIdAsync(Guid employeeId, CancellationToken ct);
    Task<Result<List<EmployeeDto>>> GetDirectReportsAsync(Guid managerId, CancellationToken ct);
    Task<Result<List<EmployeeDto>>> GetByDepartmentAsync(Guid departmentId, CancellationToken ct);
}
```

---

## Database Tables (13)

### `employees`

Central hub entity. Linked 1:1 to `users` via `user_id`.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | FK → tenants |
| `user_id` | `uuid` | FK → users (1:1) |
| `employee_number` | `varchar(20)` | Unique per tenant |
| `first_name` | `varchar(100)` | |
| `last_name` | `varchar(100)` | |
| `email` | `varchar(255)` | Work email |
| `phone` | `varchar(20)` | |
| `date_of_birth` | `date` | PII — CONFIDENTIAL |
| `gender` | `varchar(10)` | |
| `nationality_id` | `uuid` | FK → countries |
| `department_id` | `uuid` | FK → departments |
| `job_title_id` | `uuid` | FK → job_titles |
| `manager_id` | `uuid` | Self-referencing FK (nullable) |
| `legal_entity_id` | `uuid` | FK → legal_entities |
| `employment_type` | `varchar(20)` | `full_time`, `part_time`, `contract`, `intern` |
| `employment_status` | `varchar(20)` | `active`, `on_leave`, `suspended`, `terminated`, `resigned` |
| `work_mode` | `varchar(10)` | `office`, `remote`, `hybrid` |
| `hire_date` | `date` | |
| `probation_end_date` | `date` | Nullable |
| `termination_date` | `date` | Nullable |
| `avatar_file_id` | `uuid` | FK → file_records |
| `created_at` | `timestamptz` | |
| `updated_at` | `timestamptz` | |
| `is_deleted` | `boolean` | Soft delete |

**Self-referencing:** `manager_id` forms the reporting hierarchy. Handle recursive queries with CTEs.

### `employee_addresses`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `employee_id` | `uuid` | FK → employees |
| `address_type` | `varchar(20)` | `permanent`, `current`, `emergency` |
| `address_json` | `jsonb` | Street, city, state, postal, country |
| `is_primary` | `boolean` | |

### `employee_dependents`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `employee_id` | `uuid` | FK → employees |
| `name` | `varchar(100)` | |
| `relationship` | `varchar(20)` | `spouse`, `child`, `parent`, `other` |
| `date_of_birth` | `date` | |
| `is_emergency_contact` | `boolean` | |
| `phone` | `varchar(20)` | |

### `employee_qualifications`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `employee_id` | `uuid` | FK → employees |
| `qualification_type` | `varchar(20)` | `degree`, `certification`, `license` |
| `title` | `varchar(200)` | |
| `institution` | `varchar(200)` | |
| `year_obtained` | `int` | |
| `expiry_date` | `date` | Nullable |
| `document_file_id` | `uuid` | FK → file_records |

### `employee_work_history`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `employee_id` | `uuid` | FK → employees |
| `company_name` | `varchar(200)` | |
| `job_title` | `varchar(100)` | |
| `start_date` | `date` | |
| `end_date` | `date` | |
| `reason_for_leaving` | `varchar(255)` | |

### `employee_salary_history`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `employee_id` | `uuid` | FK → employees |
| `effective_date` | `date` | |
| `base_salary` | `decimal(15,2)` | |
| `currency_code` | `varchar(3)` | |
| `change_reason` | `varchar(100)` | `hire`, `promotion`, `annual_review`, `adjustment` |
| `approved_by_id` | `uuid` | FK → users |

### `employee_bank_details`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `employee_id` | `uuid` | FK → employees |
| `bank_name` | `varchar(100)` | |
| `branch_name` | `varchar(100)` | |
| `account_number_encrypted` | `bytea` | **Encrypted** via `IEncryptionService` (AES-256) |
| `routing_number` | `varchar(20)` | |
| `is_primary` | `boolean` | |

### `employee_lifecycle_events`

Audit trail for promotions, transfers, salary changes, etc.

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `employee_id` | `uuid` | FK → employees |
| `event_type` | `varchar(30)` | `hired`, `promoted`, `transferred`, `salary_change`, `suspended`, `terminated`, `resigned` |
| `event_date` | `date` | |
| `details_json` | `jsonb` | Event-specific data |
| `performed_by_id` | `uuid` | FK → users |
| `created_at` | `timestamptz` | |

### `onboarding_tasks`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `employee_id` | `uuid` | FK → employees |
| `task_name` | `varchar(200)` | |
| `category` | `varchar(50)` | `documentation`, `equipment`, `training`, `access`, `orientation` |
| `assigned_to_id` | `uuid` | FK → users |
| `due_date` | `date` | |
| `status` | `varchar(20)` | `pending`, `in_progress`, `completed` |
| `completed_at` | `timestamptz` | |

### `onboarding_templates`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `name` | `varchar(100)` | |
| `department_id` | `uuid` | FK → departments (nullable — global template) |
| `tasks_json` | `jsonb` | Template task definitions |

### `offboarding_records`

| Column | Type | Notes |
|:-------|:-----|:------|
| `id` | `uuid` | PK |
| `tenant_id` | `uuid` | |
| `employee_id` | `uuid` | FK → employees |
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
| `employee_id` | `uuid` | FK → employees |
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
| `employee_id` | `uuid` | FK → employees |
| `field_name` | `varchar(100)` | |
| `field_value` | `text` | |
| `field_type` | `varchar(20)` | `text`, `number`, `date`, `boolean`, `select` |

---

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `EmployeeCreated` | New employee added | [[notifications]], [[leave]] (calculate entitlements) |
| `EmployeePromoted` | Promotion event | [[notifications]], [[payroll]] |
| `EmployeeTransferred` | Department/team change | [[notifications]] |
| `EmployeeTerminated` | Termination/resignation | [[leave]] (forfeit unused), [[payroll]] (final settlement), [[agent-gateway]] (revoke agent) |
| `EmployeeOnboardingStarted` | Onboarding initiated | [[notifications]] |
| `EmployeeOffboardingStarted` | Offboarding initiated | [[notifications]], [[documents]] |

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
| GET | `/api/v1/employees/{id}/team` | `employees:read-team` | Get direct reports |
| GET | `/api/v1/employees/{id}/lifecycle` | `employees:read` | Lifecycle events |
| POST | `/api/v1/employees/{id}/onboarding` | `employees:write` | Start onboarding |
| POST | `/api/v1/employees/{id}/offboarding` | `employees:write` | Start offboarding |
| GET | `/api/v1/employees/{id}/salary-history` | `payroll:read` | Salary history |
| PUT | `/api/v1/employees/{id}/bank-details` | `employees:write` | Update bank details (encrypted) |

## Features

- [[employee-profiles]] — Central employee entity, addresses, custom fields — frontend: [[employee-profiles/frontend]]
- [[employee-lifecycle]] — Promotions, transfers, suspensions, terminations, salary changes
- [[onboarding]] — Onboarding task checklists and templates
- [[offboarding]] — Offboarding records, exit interviews, penalty tracking
- [[dependents-contacts]] — Dependents and emergency contacts
- [[qualifications]] — Degrees, certifications, licenses with document upload
- [[compensation]] — Salary history and bank details (encrypted)

---

## Related

- [[multi-tenancy]] — Every employee and sub-entity is tenant-scoped
- [[data-classification]] — `date_of_birth` is PII-CONFIDENTIAL; `account_number_encrypted` is AES-256
- [[compliance]] — Salary history and lifecycle events form immutable audit trail
- [[event-catalog]] — `EmployeeCreated`, `EmployeePromoted`, `EmployeeTransferred`, `EmployeeTerminated`
- [[shared-kernel]] — `BaseEntity`, `BaseRepository` foundation
- [[migration-patterns]] — Soft-delete pattern (`is_deleted`), self-referencing `manager_id` hierarchy
- [[WEEK2-core-hr-profile]] — Profile implementation task file
- [[WEEK2-core-hr-lifecycle]] — Lifecycle implementation task file

See also: [[module-catalog]], [[infrastructure]], [[org-structure]], [[leave]], [[payroll]]
