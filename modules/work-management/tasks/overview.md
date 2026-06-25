# Task Management

**Module:** Work Management
**Feature:** Task Management
**Namespace:** `WorkManagement.Tasks`
**Owner:** DEV3
**Tables:** 13

---

## Purpose

Tasks are the atomic unit of work in Work Management. Every task belongs to a project, and the project belongs to one workspace. Phase 1 tasks support subtasks, assignments, checklists, custom fields, approval gates, watchers, inter-task links, and simple Kanban/List/Calendar views. Sprint, advanced board, epic, version, and story-point fields are retained for Phase 2 planning compatibility and must not create active Phase 1 Planner screens.

Task authority is context-bound. A user with `tasks:write` can create or assign tasks only inside a project where they have local authority. The task's workspace context is inherited from the project. Reporting hierarchy may appear as non-authoritative context, but it must not grant task authority or assignment rights.

---

## Database Tables

### `tasks`

Key columns: `project_id`, `workspace_id`, `tenant_id`, `title`, `description`, `status` (`todo`, `in_progress`, `in_review`, `done`, `cancelled`), `priority` (`low`, `medium`, `high`, `urgent`), `parent_task_id`, `epic_id` (Phase 2), `sprint_id` (Phase 2), `version_id` (Phase 2), `due_date`, `story_points` (Phase 2), `short_id`, `is_archived`, `type`, `created_by_id`.


### `task_assignments`

Key columns: `task_id`, `user_id`, `employee_id`, `assigned_by_id`, `assigned_at`, `availability_status`, `availability_checked_at`, `availability_warning`. Multiple employees can be assigned to one task.

`employee_id` is required in Phase 1 and is resolved from `employees.user_id`. Assignment creation validates active employment and checks approved time_off/calendar conflicts.

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

### `boards` (Phase 2 advanced planning support)

Key columns: `project_id`, `workspace_id`, `name`, `board_type`, `sprint_id`, `user_id`.

### `board_columns` (Phase 2 advanced planning support)

Key columns: `board_id`, `name`, `status_key`, `position`, `wip_limit`.

### `board_task_positions` (Phase 2 advanced planning support)

Key columns: `board_id`, `column_id`, `task_id`, `position`.

---

## Key Business Rules

1. Tasks are project-scoped; `project_id` is immutable after creation.
2. Subtasks: `parent_task_id` self-FK, max recommended depth = 3 (not enforced in DB, UI prevents deeper nesting).
3. Status transitions are validated server-side; e.g. cannot go `done` to `in_progress` without re-opening.
4. When `task_approvals` is enabled on a project: status to `done` requires an approved `task_approvals` row.
5. `short_id` generated from `project.identifier` plus auto-increment per project (e.g. `TASK-123`). Immutable after creation.
6. Custom fields are project-level definitions; values are per-task.
7. Phase 1 Kanban view groups tasks by `tasks.status`; Phase 2 advanced boards may update `tasks.status` and `board_task_positions` in one transaction.
8. Assignment APIs must reject inactive/deleted employees and users without employee records in Phase 1.
9. Assignment APIs call Time Off + Calendar availability checks before writing `task_assignments`. Approved Time Off creates `availability_status = on_leave` and a warning by default; tenant policy may hard-block it.
10. Employee offboarding deactivates future assignability and removes active watchers where required, while preserving historical task rows.
11. When a task has `workspace_id`, it must match the owning `projects.workspace_id` unless a later Phase 2 rule explicitly reactivates multi-workspace project participation.
12. Creating a task requires `tasks:write` and active project membership or approved scoped project authority.
13. Assignment requires the assignee to be an active project member.
14. Reporting-manager relationship does not grant task assignment rights.
15. Project local administration context can allow assignment to active project members, subject to project policy.

## Assignment Decision Flow

When a user assigns a task:

1. Verify module entitlement and `tasks:write`.
2. Verify the actor can access the project through `project_members` or an approved scoped grant.
3. Verify the task's `workspace_id`, when present, matches `projects.workspace_id`.
4. Verify the actor has task authority in that project context.
5. Verify the assignee is active and belongs to the project.
6. Run time_off/calendar availability checks.
7. Write `task_assignments` or return a scoped 403 with no leaked employee/project details.

---

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `TaskCreatedEvent` | Task created | Notifications, IDE tag confirmation |
| `TaskStatusChangedEvent` | Status updated | Notifications; Phase 2 sprint burndown snapshot trigger when planning is enabled |
| `TaskAssignedEvent` | Assignee changed | Notifications, Calendar/Time Off availability audit |
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
