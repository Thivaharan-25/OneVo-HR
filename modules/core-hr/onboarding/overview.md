# Onboarding

**Module:** Core HR  
**Feature:** Onboarding

---

## Purpose

Manages onboarding checklist tasks generated from reusable Checklist Templates. Checklist Templates are shared lifecycle templates and support both onboarding and offboarding.

## Database Tables

### `employee_checklist_tasks`
Per-employee lifecycle checklist tasks: `template_id`, `lifecycle_type`, `task_title`, `owner_type`, `sequence`, `assigned_to_id`, `due_date`, `status`.

### `checklist_templates`
Reusable templates with `template_type` (`onboarding` or `offboarding`) and `tasks_json`. Can be global or department-specific.

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `EmployeeOnboardingStarted` | Onboarding initiated | [[modules/notifications/overview\|Notifications]] |

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
