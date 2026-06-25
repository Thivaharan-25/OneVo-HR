# Resource Management

**Module:** WorkSync
**Feature:** Resource Management
**Namespace:** `WorkSync.Resources`
**Owner:** DEV5
**Tables:** 3

---

## Purpose

Resource management tracks capacity planning: how much of each user's time is allocated to which projects over a date range, and temporary overrides to their baseline availability. Combined with time off data, it feeds availability calculations for Phase 2 sprint planning.

---

## Database Tables

### `resource_plans`
Key columns: `workspace_id`, `tenant_id`, `project_id`, `name`, `start_date`, `end_date`, `created_by_id`.

Container for a set of allocations for a project/period.

### `resource_allocations`
Key columns: `resource_plan_id`, `project_id`, `user_id`, `start_date`, `end_date`, `allocation_percentage` (0-100), `role_description`, `notes`.

A user can have multiple allocations across different projects. Sum of `allocation_percentage` across concurrent allocations should not exceed 100 - validated at application layer (warning, not hard block).

### `resource_availability_overrides`
Temporary changes to a user's available hours. Key columns: `user_id`, `workspace_id`, `date_from`, `date_to`, `available_hours_per_day`, `reason`, `created_by_id`.

Overrides take precedence over baseline capacity. Used for part-time periods, secondments, etc.

---

## Time Off Conversion Rule

Work Management may display and calculate capacity in hours for planning readability. Time Off remains the source of truth in minutes. Any `derived_time_off_hours` value used in Work Management is a derived capacity projection converted from canonical Time Off minutes (`approved_minutes / 60`). Work Management must not store or mutate Time Off balances directly. Do not read or write Time Off hour balances — Time Off does not expose hour-based source-of-truth fields.

---

## Key Business Rules

1. Availability calculation: `(available_hours_per_day * working_days) - derived_time_off_hours`. `derived_time_off_hours` is calculated from approved Time Off minutes for the same period.
2. Overrides take precedence over default capacity from HR employee contract.
3. `time_off_requests` (HR Pillar 1) feed into availability — `ITimeOffService.GetApprovedMinutesAsync()` provides approved Time Off minutes for a period, which Work Management converts to hours for capacity planning.
4. Over-allocation warning (> 100%): shown as warning in UI, not a hard block.
5. Resource plans are project-scoped. Roadmap aggregation is Phase 2 only.

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

- [[modules/work-management/planning/overview|Planning]] - sprint capacity uses availability
- [[modules/time-off/overview|Time Off]] - Approved Time Off minutes converted to derived_time_off_hours for availability calculation
- [[database/schemas/wms-project-management|WMS Project Management Schema]] - resource section
- [[Userflow/Work-Management/resource-flow.md|Resource Management User Flow]]
- [[current-focus/DEV5-wms-foundation|DEV5 Task 5]]
