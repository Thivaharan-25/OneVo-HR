# Employee Lifecycle

**Module:** Core HR  
**Feature:** Employee Lifecycle

---

## Purpose

Audit trail for promotions, within-company transfers, salary changes, suspensions, terminations, and resignations. Cross-company transfer does not move the source employee record between tenants; it records source-side lifecycle history and creates or activates a separate target-tenant employee record after approval.

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
| `EmployeeCreated` | New employee added | [[modules/notifications/overview\|Notifications]], [[modules/leave/overview\|Leave]] |
| `EmployeePromoted` | Promotion event | [[modules/notifications/overview\|Notifications]], [[modules/payroll/overview\|Payroll]] |
| `EmployeeTransferred` | Department/team change inside one tenant | [[modules/notifications/overview\|Notifications]] |
| `CrossCompanyTransferRequested` | Transfer case starts between connected tenants | [[modules/shared-platform/workflow-engine/overview\|Workflow Engine]], [[modules/notifications/overview\|Notifications]] |
| `CrossCompanyTransferAccepted` | Target tenant accepts and creates/activates its own employee record | [[modules/shared-platform/workflow-engine/overview\|Workflow Engine]], [[modules/notifications/overview\|Notifications]] |
| `EmployeeTerminated` | Termination/resignation | [[modules/leave/overview\|Leave]], [[modules/payroll/overview\|Payroll]], [[modules/agent-gateway/overview\|Agent Gateway]] |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/employees/{id}/lifecycle` | `employees:read` | Lifecycle events |

## Related

- [[modules/core-hr/overview|Core HR Module]]
- [[modules/core-hr/employee-profiles/overview|Employee Profiles]]
- [[modules/core-hr/onboarding/overview|Onboarding]]
- [[modules/core-hr/offboarding/overview|Offboarding]]
- [[modules/core-hr/compensation/overview|Compensation]]
- [[modules/core-hr/qualifications/overview|Qualifications]]
- [[modules/core-hr/dependents-contacts/overview|Dependents Contacts]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[security/compliance|Compliance]]
- [[backend/shared-kernel|Shared Kernel]]
- [[code-standards/logging-standards|Logging Standards]]
- [[current-focus/DEV2-core-hr-lifecycle|DEV2: Core HR Lifecycle]]
