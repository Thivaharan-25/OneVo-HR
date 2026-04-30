# Schema: WMS — Task Management

**Module:** `WorkSync.Tasks` + `WorkSync.Boards`
**Phase:** 1
**Owner:** DEV6

---

## `tasks` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `project_id` | uuid | FK → projects |
| `workspace_id` | uuid | FK → workspaces |
| `tenant_id` | uuid | FK → tenants |
| `parent_task_id` | uuid | FK → tasks, nullable — subtasks |
| `epic_id` | uuid | FK → epics, nullable |
| `milestone_id` | uuid | FK → milestones, nullable |
| `title` | varchar(500) | |
| `description` | text | nullable — rich text / markdown |
| `task_type` | varchar(20) | task / bug / story / feature |
| `status` | varchar(30) | todo / in_progress / in_review / done / cancelled |
| `priority` | varchar(20) | low / medium / high / critical |
| `story_points` | int | nullable |
| `due_date` | date | nullable |
| `started_at` | timestamptz | nullable — when status changed to in_progress |
| `completed_at` | timestamptz | nullable — when status changed to done |
| `created_by` | uuid | FK → users |
| `created_at` | timestamptz | |
| `updated_at` | timestamptz | |

**Indexes:** `(project_id, status)`, `(workspace_id)`, `(tenant_id)`, `(parent_task_id)`, `(due_date)` where not null

---

## `task_assignments` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `task_id` | uuid | FK → tasks |
| `user_id` | uuid | FK → users |
| `assigned_by` | uuid | FK → users |
| `assigned_at` | timestamptz | |

**Unique:** `(task_id, user_id)`

---

## `task_checklists` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `task_id` | uuid | FK → tasks |
| `title` | varchar(255) | |
| `position` | int | |
| `created_at` | timestamptz | |

---

## `task_checklist_items` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `checklist_id` | uuid | FK → task_checklists |
| `text` | varchar(500) | |
| `is_checked` | boolean | default false |
| `position` | int | |
| `checked_by` | uuid | FK → users, nullable |
| `checked_at` | timestamptz | nullable |

---

## `task_tags` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `task_id` | uuid | FK → tasks |
| `label_id` | uuid | FK → labels |

**PK:** `(task_id, label_id)`

---

## `task_approvals` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `task_id` | uuid | FK → tasks |
| `requested_by` | uuid | FK → users |
| `approver_id` | uuid | FK → users |
| `status` | varchar(20) | pending / approved / rejected |
| `comment` | text | nullable |
| `decided_at` | timestamptz | nullable |

---

## `task_watchers` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `task_id` | uuid | FK → tasks |
| `user_id` | uuid | FK → users |

**PK:** `(task_id, user_id)`

---

## `task_links` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `source_task_id` | uuid | FK → tasks |
| `target_task_id` | uuid | FK → tasks |
| `link_type` | varchar(30) | blocks / is_blocked_by / relates_to / duplicates |

---

## `custom_fields` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `project_id` | uuid | FK → projects |
| `name` | varchar(100) | |
| `field_type` | varchar(20) | text / number / date / select / multiselect / user |
| `options_json` | jsonb | nullable — for select/multiselect options |
| `position` | int | |
| `is_required` | boolean | default false |

---

## `custom_field_values` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `task_id` | uuid | FK → tasks |
| `field_id` | uuid | FK → custom_fields |
| `value_text` | text | nullable |
| `value_number` | numeric(18,4) | nullable |
| `value_date` | date | nullable |
| `value_json` | jsonb | nullable — for multiselect / user arrays |

**Unique:** `(task_id, field_id)`

---

## `boards` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `project_id` | uuid | FK → projects |
| `name` | varchar(100) | |
| `type` | varchar(20) | kanban / scrum / list |
| `is_default` | boolean | default false |
| `created_at` | timestamptz | |

---

## `board_columns` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `board_id` | uuid | FK → boards |
| `name` | varchar(50) | |
| `status_key` | varchar(30) | Maps to tasks.status (todo/in_progress/in_review/done/cancelled) |
| `position` | int | Column order on board |
| `wip_limit` | int | nullable — max tasks allowed in column |
| `color` | varchar(20) | nullable |

**Note:** Each board has its own column configuration. Moving a task between columns updates `tasks.status` via the `status_key` mapping.

---

## `board_task_positions` — Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `board_id` | uuid | FK → boards |
| `column_id` | uuid | FK → board_columns |
| `task_id` | uuid | FK → tasks |
| `position` | int | Card order within the column |

**Unique:** `(board_id, task_id)` — a task appears on a board in exactly one column at a time
