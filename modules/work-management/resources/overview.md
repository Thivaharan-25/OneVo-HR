# Resource Management

**Module:** WorkSync
**Feature:** Resource Management
**Namespace:** `WorkSync.Resources`
**Owner:** DEV5
**Tables:** 3

---

## Purpose

Resource management tracks capacity planning: how much of each user's time is allocated to which projects over a date range, and temporary overrides to their baseline availability. Combined with leave data, it feeds availability calculations for sprint planning.

---

## Database Tables

### `resource_plans`
Key columns: `workspace_id`, `tenant_id`, `project_id`, `name`, `start_date`, `end_date`, `created_by_id`.

Container for a set of allocations for a project/period.

### `resource_allocations`
Key columns: `resource_plan_id`, `project_id`, `user_id`, `start_date`, `end_date`, `allocation_percentage` (0–100), `role_description`, `notes`.

A user can have multiple allocations across different projects. Sum of `allocation_percentage` across concurrent allocations should not exceed 100 — validated at application layer (warning, not hard block).

### `resource_availability_overrides`
Temporary changes to a user's available hours. Key columns: `user_id`, `workspace_id`, `date_from`, `date_to`, `available_hours_per_day`, `reason`, `created_by_id`.

Overrides take precedence over baseline capacity. Used for part-time periods, secondments, etc.

---

## Key Business Rules

1. Availability calculation: `(available_hours_per_day × working_days) - leave_days × hours_per_day`.
2. Overrides take precedence over default capacity from HR employee contract.
3. `leave_requests` (HR Pillar 1) feed into availability — `IEmployeeService.GetLeaveAsync()` provides leave days for a period.
4. Over-allocation warning (> 100%): shown as warning in UI, not a hard block.
5. Resource plans are project-scoped; roadmap view aggregates across plans.

---

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `ResourceOverAllocatedEvent` | Total allocation > 100% for a user | Warning notification to PM |

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/projects/{id}/resource-plan` | `resources:read` | Get resource plan |
| POST | `/api/v1/projects/{id}/resource-plan` | `resources:manage` | Create/update plan |
| GET | `/api/v1/projects/{id}/resource-plan/allocations` | `resources:read` | List allocations |
| POST | `/api/v1/projects/{id}/resource-plan/allocations` | `resources:manage` | Add allocation |
| PATCH | `/api/v1/allocations/{id}` | `resources:manage` | Update allocation |
| POST | `/api/v1/workspaces/{wsId}/availability-overrides` | `resources:manage` | Add override |
| GET | `/api/v1/workspaces/{wsId}/availability` | `resources:read` | Get availability overview |

---

## Related

- [[modules/work-management/planning/overview|Planning]] — sprint capacity uses availability
- [[modules/leave/overview|Leave]] — leave days feed availability calc
- [[database/schemas/wms-project-management|WMS Project Management Schema]] — resource section
- [[Userflow/Work-Management/resource-flow.md|Resource Management User Flow]]
- [[current-focus/DEV5-wms-foundation|DEV5 Task 5]]
