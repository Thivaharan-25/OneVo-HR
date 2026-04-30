# Planning (Sprints, Boards, Roadmaps)

**Module:** WorkSync
**Feature:** Planning
**Namespace:** `WorkSync.Planning`
**Owner:** DEV6
**Tables:** 10

---

## Purpose

Planning covers three related capabilities: Sprint Planning (time-boxed iteration management with burndown tracking), Boards (Kanban-style task visualisation with WIP limits), and Roadmaps (timeline view across epics and milestones). Roadmaps are **Phase 1** — required by WorkSync Phase 4 user flows.

---

## Database Tables

### `sprints`
Key columns: `project_id`, `workspace_id`, `tenant_id`, `name`, `goal`, `status` (`planning`, `active`, `completed`), `start_date`, `end_date`, `velocity`, `completed_at`.

Only one sprint per project can have `status = active` at a time — enforced at application layer.

### `sprint_backlog_items`
Controls what tasks are in a sprint. Key columns: `sprint_id`, `task_id`, `added_at`, `added_by_id`, `removed_at` (nullable — null = still in sprint).

The authoritative sprint membership record. `tasks.sprint_id` is a denormalised reference for query convenience only.

### `sprint_daily_snapshots`
Burndown chart data written nightly by Hangfire. Key columns: `sprint_id`, `snapshot_date`, `total_story_points`, `completed_story_points`, `remaining_story_points`, `added_story_points`, `removed_story_points`.

One row per sprint per day. Burndown chart reads these ordered by `snapshot_date`.

### `sprint_reports`
Post-sprint summary. Key columns: `sprint_id`, `completed_points`, `total_points`, `completion_rate`, `velocity`, `summary_json`, `generated_at`.

### `boards`
Key columns: `project_id`, `workspace_id`, `name`, `board_type` (`kanban`, `scrum`), `sprint_id` (nullable — scrum boards filter by sprint), `user_id` (nullable — null for project boards, set for personal boards).

### `board_columns`
Key columns: `board_id`, `name`, `status_key` (maps 1:1 to a valid `tasks.status` value), `position`, `wip_limit` (nullable — enforced at application layer).

### `board_task_positions`
Stores card drag-order within a column. Key columns: `board_id`, `column_id`, `task_id`, `position` (float — allows insertion without reindex).

Moving a card on the board: (1) UPDATE `tasks.status = column.status_key`, (2) UPDATE `board_task_positions`. Both in one transaction.

### `roadmaps`
Key columns: `workspace_id`, `tenant_id`, `name`, `description`, `start_date`, `end_date`, `is_shared`.

Workspace-scoped. Items reference project-level entities.

### `roadmap_items`
Key columns: `roadmap_id`, `entity_type` (`Epic`, `Milestone`, `Sprint`), `entity_id`, `start_date`, `end_date`, `color`, `position`.

Polymorphic reference: `entity_type` + `entity_id` point to the relevant table.

### `baselines`
Snapshots of roadmap state at a point in time. Key columns: `roadmap_id`, `name`, `snapshot_json`, `created_at`, `created_by_id`.

Used for baseline comparison (planned vs actual timeline).

---

## Key Business Rules

1. Only one `active` sprint per project — enforced at application layer before activation.
2. `sprint_backlog_items` controls sprint membership — NOT `tasks.sprint_id` alone.
3. Sprint complete: incomplete items removed from sprint (`sprint_backlog_items.removed_at = now()`), moved back to backlog.
4. `board_columns.status_key` must map to a valid `tasks.status` enum value — validated on column create/update.
5. WIP limit: if `wip_limit` is set, count current tasks in column, reject move if `>= wip_limit`.
6. `board_task_positions.position` is float — allows insertion between positions without full reindex.
7. Burndown snapshots written nightly by Hangfire; gap days (weekends) still get a snapshot row.
8. Roadmaps are Phase 1 for WorkSync (not Phase 2) — required by WorkSync Phase 4 user flows.

---

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `SprintActivatedEvent` | Sprint status → active | Notifications, IDE SignalR `sprint:updated` |
| `SprintCompletedEvent` | Sprint marked complete | Report generation (Hangfire), Notifications |
| `SprintDailySnapshotEvent` | Nightly Hangfire job | Writes `sprint_daily_snapshots` row |
| `BoardCardMovedEvent` | Task status updated via board | `tasks.status` updated, `board_task_positions` updated |

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/projects/{id}/sprints` | `sprints:read` | List sprints |
| POST | `/api/v1/projects/{id}/sprints` | `sprints:manage` | Create sprint |
| PATCH | `/api/v1/sprints/{id}/activate` | `sprints:manage` | Activate sprint |
| PATCH | `/api/v1/sprints/{id}/complete` | `sprints:manage` | Complete sprint |
| GET | `/api/v1/sprints/{id}/burndown` | `sprints:read` | Burndown chart data |
| GET | `/api/v1/projects/{id}/boards` | `tasks:read` | List boards |
| POST | `/api/v1/projects/{id}/boards` | `projects:manage` | Create board |
| PATCH | `/api/v1/boards/{id}/tasks/{taskId}/move` | `tasks:write` | Move card |
| GET | `/api/v1/workspaces/{wsId}/roadmaps` | `roadmaps:read` | List roadmaps |
| POST | `/api/v1/workspaces/{wsId}/roadmaps` | `roadmaps:write` | Create roadmap |

---

## Related

- [[modules/work-management/tasks/overview|Task Management]]
- [[modules/work-management/projects/overview|Project Management]]
- [[database/schemas/wms-planning|WMS Planning Schema]]
- [[Userflow/Work-Management/planning-flow.md|Sprint Planning User Flow]]
- [[current-focus/DEV6-tasks-boards-planning|DEV6 Tasks 2, 3, 4]]
