# Planning (Phase 2: Planner, Boards, Advanced Roadmaps)

**Module:** Work Management
**Feature:** Planning (Phase 2)
**Namespace:** `WorkManagement.Planning`
**Owner:** DEV3
**Tables:** 8

---

## Purpose

Planning is deferred to Phase 2. Phase 1 Work must not expose Planner, sprint planning, Goals/OKR, advanced roadmap, or advanced work-planning screens. Phase 1 work execution uses Projects, Work Items, Documents, Project Members, Project Settings, and Worklogs only.

---

## Database Tables

### `sprints`

Key columns: `project_id`, `workspace_id`, `tenant_id`, `name`, `goal`, `status` (`planning`, `active`, `completed`), `start_date`, `end_date`, `velocity`, `completed_at`.

Only one sprint per project can have `status = active` at a time; enforced at application layer.

### `sprint_backlog_items`

Controls what tasks are in a sprint. Key columns: `sprint_id`, `task_id`, `added_at`, `added_by_id`, `removed_at` (nullable; null = still in sprint).

The authoritative sprint membership record. `tasks.sprint_id` is a denormalised reference for query convenience only.

### `sprint_daily_snapshots`

Burndown chart data written nightly by Hangfire. Key columns: `sprint_id`, `snapshot_date`, `total_story_points`, `completed_story_points`, `remaining_story_points`, `added_story_points`, `removed_story_points`.

### `sprint_reports`

Post-sprint summary. Key columns: `sprint_id`, `completed_points`, `total_points`, `completion_rate`, `velocity`, `summary_json`, `generated_at`.

`summary_json` stores aggregate summary only. Contributor metrics are typed in `sprint_report_contributors` for HR reporting.

### `sprint_report_contributors`

Typed contributor rows. Key columns: `sprint_report_id`, `user_id`, `employee_id`, `tasks_completed`, `story_points_completed`, `rank`.

### `roadmaps`

Key columns: `workspace_id`, `tenant_id`, `name`, `description`, `start_date`, `end_date`, `is_shared`, `created_by_id`.

### `roadmap_items`

Key columns: `roadmap_id`, `entity_type` (`Epic`, `Milestone`, `Sprint`), `entity_id`, `start_date`, `end_date`, `color`, `position`.

### `baselines`

Snapshots of roadmap state at a point in time. Key columns: `roadmap_id`, `name`, `snapshot_json`, `created_at`, `created_by_id`.

---

## Key Business Rules

1. Only one `active` sprint per project; enforced at application layer before activation.
2. `sprint_backlog_items` controls sprint membership, not `tasks.sprint_id` alone.
3. Sprint complete: incomplete items removed from sprint (`sprint_backlog_items.removed_at = now()`), moved back to backlog.
4. `board_columns.status_key` must map to a valid `tasks.status` enum value; validated on column create/update.
5. WIP limit rejects a move when the destination column already reached its limit.
6. `board_task_positions.position` is float to allow insertion between positions without full reindex.
7. Burndown snapshots written nightly by Hangfire; gap days (weekends) still get a snapshot row.
8. Roadmaps are Phase 2 and must not appear in Phase 1 customer navigation.
9. Sprint planning surfaces assignment availability warnings from `task_assignments`; planners can see when a proposed assignee is on approved time_off or blocked by calendar.
10. Sprint reports write contributor metrics to `sprint_report_contributors`, not opaque JSON.

---

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `SprintActivatedEvent` | Sprint status -> active | Notifications, IDE SignalR `sprint:updated` |
| `SprintCompletedEvent` | Sprint marked complete | Report generation (Hangfire), Notifications |
| `SprintDailySnapshotEvent` | Nightly Hangfire job | Writes `sprint_daily_snapshots` row |
| `SprintReportGeneratedEvent` | Sprint report generated | Writes `sprint_report_contributors` |
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
| GET | `/api/v1/sprints/{id}/report/contributors` | `sprints:read` | Typed sprint contributor metrics |
| GET | `/api/v1/projects/{id}/boards` | `tasks:read` | List boards |
| POST | `/api/v1/projects/{id}/boards` | `projects:write` | Create board |
| PATCH | `/api/v1/boards/{id}/tasks/{taskId}/move` | `tasks:write` | Move card |
| GET | `/api/v1/workspaces/{wsId}/roadmaps` | `roadmaps:read` | List roadmaps |
| POST | `/api/v1/workspaces/{wsId}/roadmaps` | `roadmaps:write` | Create roadmap |

---

## Related

- [[modules/work-management/tasks/overview|Task Management]]
- [[modules/work-management/projects/overview|Project Management]]
- [[database/schemas/wms-planning|WMS Planning Schema]]
- [[database/cross-module-relationships|Cross-Module Relationships]]
- [[Userflow/Work-Management/planning-flow.md|Sprint Planning User Flow]]
- [[current-focus/DEV3|DEV3 Task 2]]
