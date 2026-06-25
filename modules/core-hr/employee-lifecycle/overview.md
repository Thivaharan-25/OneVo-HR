# Employee Lifecycle

**Module:** Core HR  
**Feature:** Employee Lifecycle

---

## Purpose

Audit trail for promotions, transfers, salary changes, suspensions, terminations, and resignations. Phase 1 transfer/promotion approvals are lightweight module-owned approvals routed through Org Structure management coverage, not Workflow Engine flows.

## Database Tables

### `employee_lifecycle_events`

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


### `employee_assignment_history`

Effective-dated assignment history for department and position. Current profile snapshots are stored on `employees`; reporting history is resolved from `position_assignments` and `position_reporting_history` by date.

### `employee_transfers`

Transfer request records. Approved transfers apply on their effective date, close/create `position_assignments`, update current employee assignment snapshots, create assignment history, and publish `EmployeeTransferred`.

### Assignment Model

- Primary Employment Assignment: one active row; controls primary legal entity, Time Off policy, attendance policy, work schedule, holiday calendar, and payroll/statutory context.
- Additional Authority Assignment: optional rows; may grant role/access/approval authority only.
- No two active employment assignments inside the same legal entity.
## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `EmployeeCreated` | New employee added | [[modules/notifications/overview\|Notifications]], [[modules/time-off/overview\|Time Off]] |
| `EmployeePromoted` | Promotion event | [[modules/notifications/overview\|Notifications]], [[modules/payroll/overview\|Payroll]] |
| `EmployeeTransferred` | Employee assignment change inside one tenant | [[modules/notifications/overview\|Notifications]] |
| `EmployeeTransferApprovalRequested` | Transfer changes sensitive position-derived access or actor lacks authority | [[modules/notifications/overview\|Notifications]] |
| `EmployeePromotionApprovalRequested` | Promotion changes sensitive position-derived access or actor lacks authority | [[modules/notifications/overview\|Notifications]] |
| `EmployeeTerminated` | Termination/resignation | [[modules/time-off/overview\|Time Off]], [[modules/payroll/overview\|Payroll]], [[modules/agent-gateway/overview\|Agent Gateway]] |

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
