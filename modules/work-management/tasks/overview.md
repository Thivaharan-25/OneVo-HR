# Task Management

**Module:** Work Management
**Feature:** Task Management
**Namespace:** `WorkManagement.Tasks`
**Owner:** DEV3
**Tables:** 13

---

## Purpose

Tasks are the atomic unit of work in Work Management. Every task belongs to a project. Tasks support subtasks, assignments, checklists, custom fields, approval gates, watchers, and inter-task links.

---

## Database Tables

### `tasks`

Key columns: `project_id`, `workspace_id`, `tenant_id`, `title`, `description`, `status` (`todo`, `in_progress`, `in_review`, `done`, `cancelled`), `priority` (`low`, `medium`, `high`, `urgent`), `parent_task_id`, `epic_id`, `sprint_id`, `version_id`, `due_date`, `story_points`, `short_id`, `is_archived`, `type`, `created_by_id`.

### `task_assignments`

Key columns: `task_id`, `user_id`, `employee_id`, `assigned_by_id`, `assigned_at`, `availability_status`, `availability_checked_at`, `availability_warning`. Multiple employees can be assigned to one task.

`employee_id` is required in Phase 1 and is resolved from `employees.user_id`. Assignment creation validates active employment and checks approved leave/calendar conflicts.

### `task_checklists`

Key columns: `task_id`, `title`, `position`. Groups checklist items.

### `task_checklist_items`

Key columns: `checklist_id`, `title`, `is_checked`, `checked_by_id`, `checked_at`, `position`.

### `task_tags`

Key columns: `task_id`, `label_id` (FK -> labels). Many-to-many.

### `task_approvals`

Gates status transition to `done` when the project has approval flow enabled. Key columns: `task_id`, `requested_by_id`, `approver_id`, `approver_employee_id`, `status` (`pending`, `approved`, `rejected`), `decided_at`, `comments`.

### `task_watchers`

Key columns: `task_id`, `user_id`, `employee_id`; watchers are notified on all task activity and can be filtered by HR state.

### `task_links`

Inter-task dependency links. Key columns: `source_task_id`, `target_task_id`, `link_type` (`blocks`, `blocked_by`, `duplicates`, `relates_to`).

### `custom_fields`

Project-level field definitions. Key columns: `project_id`, `name`, `field_type` (`text`, `number`, `date`, `select`, `multi_select`, `user`, `checkbox`), `options_json`, `is_required`, `position`.

### `custom_field_values`

Per-task values. Key columns: `task_id`, `custom_field_id`, `text_value`, `number_value`, `date_value`, `user_value`, `select_values_json`.

### `boards`

Key columns: `project_id`, `workspace_id`, `name`, `board_type`, `sprint_id`, `user_id`.

### `board_columns`

Key columns: `board_id`, `name`, `status_key`, `position`, `wip_limit`.

### `board_task_positions`

Key columns: `board_id`, `column_id`, `task_id`, `position`.

---

## Key Business Rules

1. Tasks are project-scoped; `project_id` is immutable after creation.
2. Subtasks: `parent_task_id` self-FK, max recommended depth = 3 (not enforced in DB, UI prevents deeper nesting).
3. Status transitions are validated server-side; e.g. cannot go `done` to `in_progress` without re-opening.
4. When `task_approvals` is enabled on a project: status to `done` requires an approved `task_approvals` row.
5. `short_id` generated from `project.identifier` plus auto-increment per project (e.g. `TASK-123`). Immutable after creation.
6. Custom fields are project-level definitions; values are per-task.
7. Moving a task to a board column updates `tasks.status` and `board_task_positions` in one transaction.
8. Assignment APIs must reject inactive/deleted employees and users without employee records in Phase 1.
9. Assignment APIs call Leave + Calendar availability checks before writing `task_assignments`. Approved leave creates `availability_status = on_leave` and a warning by default; tenant policy may hard-block it.
10. Employee offboarding deactivates future assignability and removes active watchers where required, while preserving historical task rows.

---

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `TaskCreatedEvent` | Task created | Notifications, IDE tag confirmation |
| `TaskStatusChangedEvent` | Status updated | Sprint burndown snapshot trigger, Notifications |
| `TaskAssignedEvent` | Assignee changed | Notifications, Calendar/Leave availability audit |
| `TaskApprovedEvent` | `task_approvals` approved | Sets status = done |
| `TaskCompletedEvent` | Status -> done | Time log close, Reminders sync |

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/projects/{id}/tasks` | `tasks:read` | List tasks (filtered) |
| POST | `/api/v1/projects/{id}/tasks` | `tasks:write` | Create task |
| GET | `/api/v1/tasks/{id}` | `tasks:read` | Get task detail |
| PATCH | `/api/v1/tasks/{id}` | `tasks:write` | Update task |
| DELETE | `/api/v1/tasks/{id}` | `tasks:delete` | Archive task |
| PATCH | `/api/v1/tasks/{id}/status` | `tasks:write` | Update status |
| POST | `/api/v1/tasks/{id}/assignments` | `tasks:write` | Assign employee-backed user with availability check |
| POST | `/api/v1/tasks/{id}/checklists` | `tasks:write` | Add checklist |
| POST | `/api/v1/tasks/{id}/approvals` | `tasks:approve` | Submit/approve task |
| GET | `/api/v1/projects/{id}/custom-fields` | `tasks:read` | List custom fields |

---

## Related

- [[modules/work-management/planning/overview|Planning (Boards + Sprints)]]
- [[modules/work-management/projects/overview|Project Management]]
- [[modules/work-management/time/overview|Time Management]]
- [[modules/work-management/integrations/overview|Integrations]]
- [[database/schemas/wms-task-management|WMS Task Management Schema]]
- [[database/cross-module-relationships|Cross-Module Relationships]]
- [[Userflow/Work-Management/task-flow.md|Task User Flow]]
- [[current-focus/DEV3|DEV3 Task 2]]
