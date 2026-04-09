# Onboarding

**Module:** Core HR  
**Feature:** Onboarding

---

## Purpose

Manages onboarding tasks and reusable templates per department.

## Database Tables

### `onboarding_tasks`
Per-employee tasks: `task_name`, `category` (`documentation`, `equipment`, `training`, `access`, `orientation`), `assigned_to_id`, `due_date`, `status`.

### `onboarding_templates`
Reusable templates with `tasks_json`. Can be global or department-specific.

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `EmployeeOnboardingStarted` | Onboarding initiated | [[modules/notifications/overview|Notifications]] |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| POST | `/api/v1/employees/{id}/onboarding` | `employees:write` | Start onboarding |

## Related

- [[modules/core-hr/overview|Core HR Module]]
- [[modules/core-hr/employee-profiles/overview|Employee Profiles]]
- [[modules/core-hr/employee-lifecycle/overview|Employee Lifecycle]]
- [[modules/core-hr/offboarding/overview|Offboarding]]
- [[modules/core-hr/compensation/overview|Compensation]]
- [[modules/core-hr/qualifications/overview|Qualifications]]
- [[modules/core-hr/dependents-contacts/overview|Dependents Contacts]]
- [[infrastructure/multi-tenancy|Multi Tenancy]]
- [[security/auth-architecture|Auth Architecture]]
- [[backend/messaging/event-catalog|Event Catalog]]
- [[security/compliance|Compliance]]
- [[backend/shared-kernel|Shared Kernel]]
- [[current-focus/DEV2-core-hr-lifecycle|DEV2: Core HR Lifecycle]]
