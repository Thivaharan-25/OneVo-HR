# Schema: Work Management - Task Management

**Module:** `Work Management.Tasks` + `Work Management.Boards`
**Phase:** 1
**Owner:** DEV3

---

## `tasks` - Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `project_id` | uuid | FK -> projects |
| `workspace_id` | uuid | FK -> workspaces; task's team/workspace context |
| `tenant_id` | uuid | FK -> tenants |
| `parent_task_id` | uuid | FK -> tasks, nullable; subtasks |
| `epic_id` | uuid | FK -> epics, nullable |
| `milestone_id` | uuid | FK -> milestones, nullable |
| `title` | varchar(500) | |
| `description` | text | nullable; rich text / markdown |
| `task_type` | varchar(20) | task / bug / story / feature |
| `status` | varchar(30) | todo / in_progress / in_review / done / cancelled |
| `priority` | varchar(20) | low / medium / high / critical |
| `story_points` | int | nullable |
| `due_date` | date | nullable |
| `started_at` | timestamptz | nullable; when status changed to in_progress |
| `completed_at` | timestamptz | nullable; when status changed to done |
| `created_by_id` | uuid | FK -> users |
| `created_at` | timestamptz | |
| `updated_at` | timestamptz | |

**Indexes:** `(project_id, status)`, `(workspace_id)`, `(tenant_id)`, `(parent_task_id)`, `(due_date)` where not null

**Rule:** `workspace_id` must reference an active `project_workspaces` link for the task's project. It does not mean the project belongs to one workspace.

**Authority rule:** Creating or assigning a task requires the actor to have the required task permission plus local authority in the project/workspace context. Reporting hierarchy over an assignee is not enough inside another manager's workspace or project.

---

## `task_assignments` - Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `task_id` | uuid | FK -> tasks |
| `user_id` | uuid | FK -> users |
| `employee_id` | uuid | FK -> employees; required for tenant employees |
| `assigned_by_id` | uuid | FK -> users |
| `assigned_at` | timestamptz | |
| `availability_status` | varchar(20) | `available`, `on_leave`, `outside_schedule`, `inactive_employee`, `unknown` |
| `availability_checked_at` | timestamptz | nullable |
| `availability_warning` | text | nullable |

**Unique:** `(task_id, user_id)`
**Indexes:** `(employee_id)`, `(availability_status)`

**Rule:** Assignment APIs must resolve `employee_id` from `employees.user_id`, block inactive/deleted employees, and call Calendar/Leave availability checks for the task date range. Approved leave creates a warning by default; tenant policy can make it blocking.

**Assignment scope rule:** The assignee must be an active project member, a selected member from the responsible workspace, or an approved scoped participant. If the actor is relying on reporting-manager authority, the assignee must be in the actor's position-derived hierarchy and the actor must have authority in the selected workspace/project context.

---

## `task_checklists` - Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `task_id` | uuid | FK -> tasks |
| `title` | varchar(255) | |
| `position` | int | |
| `created_at` | timestamptz | |

---

## `task_checklist_items` - Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `checklist_id` | uuid | FK -> task_checklists |
| `text` | varchar(500) | |
| `is_checked` | boolean | default false |
| `position` | int | |
| `checked_by_id` | uuid | FK -> users, nullable |
| `checked_at` | timestamptz | nullable |

---

## `task_tags` - Phase 1

| Column | Type | Notes |
|---|---|---|
| `task_id` | uuid | FK -> tasks |
| `label_id` | uuid | FK -> labels |

**PK:** `(task_id, label_id)`

---

## `task_approvals` - Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `task_id` | uuid | FK -> tasks |
| `requested_by_id` | uuid | FK -> users |
| `approver_id` | uuid | FK -> users |
| `approver_employee_id` | uuid | FK -> employees |
| `status` | varchar(20) | pending / approved / rejected |
| `comment` | text | nullable |
| `decided_at` | timestamptz | nullable |

---

## `task_watchers` - Phase 1

| Column | Type | Notes |
|---|---|---|
| `task_id` | uuid | FK -> tasks |
| `user_id` | uuid | FK -> users |
| `employee_id` | uuid | FK -> employees; required for tenant employees |

**PK:** `(task_id, user_id)`
**Index:** `(employee_id)`

---

## `task_links` - Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `source_task_id` | uuid | FK -> tasks |
| `target_task_id` | uuid | FK -> tasks |
| `link_type` | varchar(30) | blocks / is_blocked_by / relates_to / duplicates |

---

## `custom_fields` - Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `project_id` | uuid | FK -> projects |
| `name` | varchar(100) | |
| `field_type` | varchar(20) | text / number / date / select / multiselect / user |
| `options_json` | jsonb | nullable; for select/multiselect options |
| `position` | int | |
| `is_required` | boolean | default false |

---

## `custom_field_values` - Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `task_id` | uuid | FK -> tasks |
| `field_id` | uuid | FK -> custom_fields |
| `value_text` | text | nullable |
| `value_number` | numeric(18,4) | nullable |
| `value_date` | date | nullable |
| `value_json` | jsonb | nullable; for multiselect / user arrays |

**Unique:** `(task_id, field_id)`

---

## `boards` - Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `project_id` | uuid | FK -> projects |
| `name` | varchar(100) | |
| `type` | varchar(20) | kanban / scrum / list |
| `is_default` | boolean | default false |
| `created_at` | timestamptz | |

---

## `board_columns` - Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `board_id` | uuid | FK -> boards |
| `name` | varchar(50) | |
| `status_key` | varchar(30) | Maps to tasks.status |
| `position` | int | Column order on board |
| `wip_limit` | int | nullable; max tasks allowed in column |
| `color` | varchar(20) | nullable |

**Note:** Each board has its own column configuration. Moving a task between columns updates `tasks.status` via the `status_key` mapping.

---

## `board_task_positions` - Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `board_id` | uuid | FK -> boards |
| `column_id` | uuid | FK -> board_columns |
| `task_id` | uuid | FK -> tasks |
| `position` | int | Card order within the column |

**Unique:** `(board_id, task_id)`; a task appears on a board in exactly one column at a time.
