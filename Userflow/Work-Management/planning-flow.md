# Planning - Sprints, Boards, Roadmap (Phase 2)

**Area:** Work -> Planner (`/work/planner`) and Work -> Projects -> Sprints / Roadmap (Phase 2 only)
**Trigger:** Deferred Phase 2 only. Phase 1 must not expose Planner, sprint, board, roadmap, or advanced work-planning navigation.
**Required Permission:** `sprints:read` (view); `sprints:manage` (create/edit sprints and boards)

## Purpose

Planning organises tasks into time-boxed sprints, visual boards, and a timeline roadmap. This is a deferred Phase 2 design reference. Phase 1 Work supports Projects, Work Items, Documents, Project Members, Project Settings, and Worklogs only.

Sprint planning must surface HR availability. If assigned employees are on approved time off or blocked by calendar, the planner sees the warning before activating the sprint.

## Key Entities

| Entity | Role |
|---|---|
| `SPRINT` | Time-boxed work period: start date, end date, tasks |
| `SPRINT_REPORT` | Velocity and completed points for a finished sprint |
| `SPRINT_REPORT_CONTRIBUTOR` | Typed contributor metrics linked to user and employee |
| `BOARD` | Visual task grouping: kanban or list type |
| `BOARD_VIEW` | User-specific saved view (column config, filters) |
| `ROADMAP` | Workspace-level timeline of epics and milestones |
| `ROADMAP_ITEM` | An epic or milestone placed on the roadmap |
| `VERSION` | A planned release with a target date |
| `RELEASE_CALENDAR` | Scheduled release events |
| `BASELINE` | Snapshot of the project plan at a point in time |

## Flow Steps

### Workspace Planner (`/work/planner`, Phase 2)

1. User opens Work -> Planner.
2. System loads all active sprints and boards across all projects the user is a member of.
3. User can switch between Board view and List view.
4. Filters: project, assignee, priority, label, sprint.

### Create Sprint (within a project)

1. User opens `/work/projects/[id]/sprints`.
2. User clicks "New Sprint" and enters name, start date, end date.
3. System creates `SPRINT` record linked to the project.
4. User drags tasks from the backlog into the sprint.
5. System surfaces Time Off/calendar assignment warnings for tasks assigned to unavailable employees.

### Sprint Lifecycle

```text
Planning -> Active -> Completed
```

1. **Planning**: sprint created, tasks being assigned.
2. **Active**: sprint started, tasks in progress, daily updates visible.
3. **Completed**: sprint ends, system generates `SPRINT_REPORT` plus typed `SPRINT_REPORT_CONTRIBUTOR` rows.
4. Incomplete tasks are moved back to the backlog or carried into the next sprint.

### Board View

1. User opens a project board at `/work/projects/[id]/items`.
2. Board renders tasks as cards in status columns (Open / In Progress / In Review / Closed).
3. User drags cards between columns to update task status.
4. User saves a custom column config stored as `BOARD_VIEW`.

### Roadmap

1. User opens `/work/projects/[id]/roadmap`.
2. System renders epics and milestones as a horizontal timeline.
3. User places `ROADMAP_ITEM` records by dragging epics/milestones onto the timeline.
4. Baseline snapshot can be taken to compare planned vs actual progress.

### Release Planning

1. User creates a `VERSION` (e.g., `v1.2`) with a target date.
2. User schedules the release via `RELEASE_CALENDAR`.
3. Tasks can be tagged to a version and appear grouped in the version detail.

## Connection Points

| Connects to | How |
|---|---|
| Work -> Projects | Sprints and roadmaps are sub-views of a project |
| Work -> Work Items | Tasks planned in sprints appear in Work Items for assignees |
| Time Off + Calendar | Planning shows assignment availability warnings before sprint activation |
| Calendar | Release dates from `RELEASE_CALENDAR` can appear in the Calendar unified view |
| Inbox | Sprint completion reports and release notifications land in Inbox |

## Related Flows

- [[Userflow/Work-Management/wm-overview|WMS Overview]]
- [[Userflow/Work-Management/project-flow|Project Management]]
- [[Userflow/Work-Management/task-flow|Task Management]]
