# Task: Tasks + Boards + Planning + Roadmaps + Analytics

**Assignee:** Dev 6
**Pillar:** Pillar 3 — WorkSync
**Priority:** Critical
**Dependencies:** DEV5 WorkSync Foundation (workspaces), DEV5 Projects (project_id FK), DEV1 Infrastructure (file_assets for attachments), DEV2 Auth (permissions)

---

## Task 1: Task Management

**Module:** `ONEVO.Modules.WorkSync.Tasks`
**Tables:** `tasks`, `task_assignments`, `task_checklists`, `task_checklist_items`, `task_tags`, `task_approvals`, `task_watchers`, `task_links`, `custom_fields`, `custom_field_values`
**Depends on:** DEV5 Task 1 (workspaces), DEV5 Task 2 (projects)

### Acceptance Criteria

- [ ] `tasks` table: id, project_id → projects, parent_task_id → tasks nullable (subtasks), title, description text nullable, task_type (task/bug/story/epic_task), status (todo/in_progress/in_review/done/cancelled), priority (low/medium/high/critical), story_points int nullable, due_date date nullable, created_by → users, created_at, updated_at
- [ ] `task_assignments` table: id, task_id → tasks, user_id → users, assigned_by → users, assigned_at. UNIQUE (task_id, user_id)
- [ ] `task_checklists` table: id, task_id → tasks, title, position int, created_at
- [ ] `task_checklist_items` table: id, checklist_id → task_checklists, text, is_checked boolean, position int, checked_by → users nullable, checked_at nullable
- [ ] `task_tags` table: task_id → tasks, label_id → labels. PK (task_id, label_id)
- [ ] `task_approvals` table: id, task_id → tasks, requested_by → users, approver_id → users, status (pending/approved/rejected), decided_at nullable
- [ ] `task_watchers` table: task_id → tasks, user_id → users. PK (task_id, user_id)
- [ ] `task_links` table: id, source_task_id → tasks, target_task_id → tasks, link_type (blocks/is_blocked_by/relates_to/duplicates)
- [ ] `custom_fields` table: id, project_id → projects, name, field_type (text/number/date/select/multiselect/user), options_json jsonb nullable, position int
- [ ] `custom_field_values` table: id, task_id → tasks, field_id → custom_fields, value_text text nullable, value_number numeric nullable, value_date date nullable, value_json jsonb nullable
- [ ] CRUD APIs with permission checks (`tasks:read`, `tasks:write`, `tasks:assign`)
- [ ] `GET /api/v1/projects/{id}/tasks` — list tasks with filters (status, assignee, sprint, label)
- [ ] `POST /api/v1/tasks/{id}/assign` — assign user
- [ ] `PUT /api/v1/tasks/{id}/status` — change status (triggers domain event)
- [ ] Domain events: `TaskCreatedEvent`, `TaskStatusChangedEvent`, `TaskAssignedEvent` → Notifications module
- [ ] Task status change must sync with board column when task is on a board (via `board_task_positions`)

### Backend References
- [[onevo-unified-entity-map|Entity Map]] — Section 26 WMS Task Management
- [[database/schemas/wms-task-management|WMS Task Schema]]
- [[modules/work-management/tasks|WMS Tasks spec]]

---

## Task 2: Boards + Board Columns

**Module:** `ONEVO.Modules.WorkSync.Boards`
**Tables:** `boards`, `board_columns`, `board_task_positions`
**Depends on:** Task 1 (tasks)

### Acceptance Criteria

- [ ] `boards` table: id, project_id → projects, name, type (kanban/scrum/list), is_default boolean, created_at
- [ ] `board_columns` table: id, board_id → boards, name, status_key (maps to tasks.status), position int, wip_limit int nullable, color varchar(20)
- [ ] `board_task_positions` table: id, board_id → boards, column_id → board_columns, task_id → tasks, position int. UNIQUE (board_id, task_id)
- [ ] Default Kanban board created with project — columns: To Do, In Progress, In Review, Done
- [ ] Default Scrum board created with first sprint — columns match sprint workflow
- [ ] `GET /api/v1/boards/{id}` — board with columns and tasks in column order
- [ ] `PUT /api/v1/boards/{id}/columns/{colId}/tasks/{taskId}/position` — drag task to column + position
- [ ] Moving task between columns updates `tasks.status` via domain event
- [ ] WIP limit enforcement: if `wip_limit` set, reject task move to column if at/over limit (return 409)
- [ ] Board column positions are per-board, not global — each board has its own column config
- [ ] `POST /api/v1/boards/{id}/columns` — add custom column
- [ ] `DELETE /api/v1/boards/{id}/columns/{colId}` — delete column (tasks move to preceding column)

### Backend References
- [[onevo-unified-entity-map|Entity Map]] — Section 27 WMS Planning (boards sub-section)
- [[database/schemas/wms-task-management|WMS Task Schema]]

---

## Task 3: Sprint Planning + Backlog + Burndown

**Module:** `ONEVO.Modules.WorkSync.Planning`
**Tables:** `sprints`, `sprint_backlog_items`, `sprint_daily_snapshots`, `sprint_reports`
**Depends on:** Task 1 (tasks), Task 2 (boards)

### Acceptance Criteria

- [ ] `sprints` table: id, project_id → projects, name, goal text nullable, start_date date, end_date date, status (planned/active/completed), created_at, updated_at
- [ ] `sprint_backlog_items` table: id, sprint_id → sprints, task_id → tasks, story_points int nullable, added_at, added_by → users. UNIQUE (sprint_id, task_id)
- [ ] `sprint_daily_snapshots` table: id, sprint_id → sprints, snapshot_date date, total_points int, completed_points int, remaining_points int, added_points int (scope creep), removed_points int. UNIQUE (sprint_id, snapshot_date)
- [ ] `sprint_reports` table: id, sprint_id → sprints UNIQUE, velocity numeric(8,2), completed_points int, incomplete_points int, summary_json jsonb, created_at
- [ ] Backlog = tasks in the project NOT assigned to any sprint. Ordered by priority then created_at.
- [ ] `POST /api/v1/sprints/{id}/start` — mark sprint active, create initial burndown snapshot
- [ ] `POST /api/v1/sprints/{id}/complete` — mark sprint complete, move incomplete tasks to backlog, generate `sprint_reports` row
- [ ] Hangfire job: daily burndown snapshot at 23:59 tenant time for all active sprints. Snapshot: total_points = all backlog items, completed_points = done tasks, remaining = total - completed
- [ ] `GET /api/v1/sprints/{id}/burndown` — return all snapshots ordered by date (chart data)
- [ ] `POST /api/v1/sprints/{id}/backlog` — add task to sprint backlog (also creates board_task_positions row in sprint board)
- [ ] `DELETE /api/v1/sprints/{id}/backlog/{taskId}` — remove from sprint (returns task to backlog)
- [ ] Only one active sprint per project at a time (enforce with unique constraint on status=active + project_id)

### Backend References
- [[onevo-unified-entity-map|Entity Map]] — Section 27 WMS Planning
- [[database/schemas/wms-planning|WMS Planning Schema]]

---

## Task 4: Roadmaps (Phase 1 for WorkSync)

**Module:** `ONEVO.Modules.WorkSync.Planning` (same as sprints)
**Tables:** `roadmaps`, `roadmap_items`, `baselines`
**Depends on:** Task 2 (projects), Task 3 (sprints, milestones)

> Roadmaps are marked Phase 2 in the original HR plan but are **Phase 1 for WorkSync** — the WorkSync user flow requires Team Lead to open Roadmap, view sprints on a timeline, drag them, attach versions, and save.

### Acceptance Criteria

- [ ] `roadmaps` table: id, workspace_id → workspaces, name, start_date date, end_date date, is_shared boolean, created_by → users, created_at
- [ ] `roadmap_items` table: id, roadmap_id → roadmaps, entity_type (Epic/Milestone/Sprint/Version), entity_id uuid, position int, color varchar(20) nullable
- [ ] `baselines` table: id, project_id → projects, name, snapshot_json jsonb (full task/sprint state at snapshot time), created_by → users, created_at
- [ ] `GET /api/v1/workspaces/{id}/roadmaps` — list roadmaps
- [ ] `POST /api/v1/roadmaps/{id}/items` — add epic/milestone/sprint to roadmap
- [ ] `PUT /api/v1/roadmaps/{id}/items/{itemId}/position` — reorder item on timeline
- [ ] `POST /api/v1/projects/{id}/baselines` — snapshot current project state for comparison
- [ ] Roadmap is shared within workspace by default; `is_shared = false` makes it private to creator

### Backend References
- [[onevo-unified-entity-map|Entity Map]] — Section 27 WMS Planning (roadmaps sub-section)
- [[database/schemas/wms-planning|WMS Planning Schema]]

---

## Task 5: Insight & Analytics

**Module:** `ONEVO.Modules.WorkSync.Analytics`
**Tables:** `dashboards`, `chart_widgets`, `saved_views`, `report_snapshots`, `report_exports`, `dashboard_shares`, `saved_view_shares`
**Depends on:** Task 3 (sprint_reports), Task 1 (tasks for filtering)

### Acceptance Criteria

- [ ] `dashboards` table: id, workspace_id → workspaces, name, created_by → users, is_shared boolean, created_at, updated_at
- [ ] `chart_widgets` table: id, dashboard_id → dashboards, widget_type (sprint_velocity/task_status_distribution/burndown/team_workload/time_report/resource_utilization), config_json jsonb, position_x int, position_y int, width int, height int
- [ ] `saved_views` table: id, workspace_id → workspaces, entity_type (tasks/projects/sprints), name, filter_json jsonb, sort_json jsonb, created_by → users, is_shared boolean, created_at
- [ ] `report_snapshots` table: id, workspace_id → workspaces, report_type, snapshot_json jsonb, created_at
- [ ] `report_exports` table: id, workspace_id → workspaces, export_type (csv/pdf/excel), entity_type, filter_json jsonb, file_asset_id → file_assets nullable, status (pending/ready/failed), created_at
- [ ] `dashboard_shares` table: id, dashboard_id → dashboards, shared_with_type (user/team/workspace), shared_with_id uuid, can_edit boolean, shared_by → users, shared_at
- [ ] `saved_view_shares` table: id, saved_view_id → saved_views, shared_with_type (user/team/workspace), shared_with_id uuid, shared_by → users, shared_at
- [ ] `GET /api/v1/dashboards/{id}` — dashboard with widgets
- [ ] `POST /api/v1/dashboards/{id}/share` — share to user/team/workspace
- [ ] `GET /api/v1/dashboards/{id}/widgets/{widgetId}/data` — widget data query (routed to correct report service)
- [ ] `POST /api/v1/workspaces/{id}/report-exports` — trigger async export (Hangfire job)
- [ ] Hangfire job: report export processing — generates file, uploads to Azure Blob, updates file_asset_id
- [ ] Widget data endpoints use read-optimized queries (no N+1)

### Backend References
- [[onevo-unified-entity-map|Entity Map]] — Section 37 WMS Insight & Analytics
- [[database/schemas/wms-analytics|WMS Analytics Schema]]

---

## Step 2: Frontend

### Pages to Build

```
app/(dashboard)/workspaces/[id]/
├── tasks/
│   └── page.tsx                   # Task list with filters + inline edit
├── board/
│   └── page.tsx                   # Kanban board — drag/drop columns + cards
├── backlog/
│   └── page.tsx                   # Sprint backlog + unassigned tasks
├── sprint/
│   ├── page.tsx                   # Sprint list
│   └── [sprintId]/
│       ├── board/page.tsx         # Scrum sprint board
│       └── burndown/page.tsx      # Burndown chart (recharts line chart)
├── roadmap/
│   └── page.tsx                   # Roadmap timeline (horizontal Gantt-style)
└── analytics/
    ├── page.tsx                   # Dashboard list
    └── [dashboardId]/
        └── page.tsx               # Dashboard with configurable widgets
```

### Key Userflows
- [[Userflow/Work-Management/task-creation|Task Creation]]
- [[Userflow/Work-Management/board-flow|Board + Kanban Flow]]
- [[Userflow/Work-Management/sprint-planning|Sprint Planning]]
- [[Userflow/Work-Management/burndown|Burndown Chart]]
- [[Userflow/Work-Management/roadmap|Roadmap View]]
