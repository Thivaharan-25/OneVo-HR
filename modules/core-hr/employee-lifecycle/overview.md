# Employee Lifecycle

**Module:** Core HR  
**Feature:** Employee Lifecycle

---

## Purpose

Audit trail for promotions, transfers, salary changes, suspensions, terminations, and resignations.

## Database Tables

### `employee_lifecycle_events`

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

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `EmployeeCreated` | New employee added | [[notifications]], [[leave]] |
| `EmployeePromoted` | Promotion event | [[notifications]], [[payroll]] |
| `EmployeeTransferred` | Department/team change | [[notifications]] |
| `EmployeeTerminated` | Termination/resignation | [[leave]], [[payroll]], [[agent-gateway]] |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/employees/{id}/lifecycle` | `employees:read` | Lifecycle events |

## Related

- [[core-hr|Core HR Module]]
- [[employee-profiles]]
- [[onboarding]]
- [[offboarding]]
- [[compensation]]
- [[qualifications]]
- [[dependents-contacts]]
- [[multi-tenancy]]
- [[auth-architecture]]
- [[event-catalog]]
- [[compliance]]
- [[shared-kernel]]
- [[logging-standards]]
- [[WEEK2-core-hr-lifecycle]]
