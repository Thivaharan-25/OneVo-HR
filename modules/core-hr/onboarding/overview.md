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
| `EmployeeOnboardingStarted` | Onboarding initiated | [[notifications]] |

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| POST | `/api/v1/employees/{id}/onboarding` | `employees:write` | Start onboarding |

## Related

- [[core-hr|Core HR Module]]
- [[employee-profiles]]
- [[employee-lifecycle]]
- [[offboarding]]
- [[compensation]]
- [[qualifications]]
- [[dependents-contacts]]
- [[multi-tenancy]]
- [[auth-architecture]]
- [[event-catalog]]
- [[compliance]]
- [[shared-kernel]]
- [[WEEK2-core-hr-lifecycle]]
