# ADE Reading Flow: Dev 6 — Start to End

**What this document is:** The exact sequence of files an ADE agent reads, in order, when
given the command: "You are Dev 6. Build all your tasks."

This covers the full journey — orchestrator startup, base context loading, each of Dev 6's
5 tasks across Task Management, Boards, Sprint Planning, Roadmaps, and Analytics.

---

## Phase 0: Orchestrator Startup

The orchestrator runs first and determines what to do. It reads:

```
1. ADE-START-HERE.md                   ← Platform overview, all 3 pillars, IDE Extension
2. current-focus/README.md             ← Task assignment table: Dev 6 has 5 tasks
```

From `current-focus/README.md`, the orchestrator extracts:

| Task # | Module | Key Tables |
|:-------|:-------|:-----------|
| 1 | Task Management | tasks, task_assignments, checklists, custom_fields, board_columns, board_task_positions |
| 2 | Boards | boards, board_columns, board_task_positions |
| 3 | Sprint Planning | sprints, sprint_backlog_items, sprint_daily_snapshots, sprint_reports |
| 4 | Roadmaps | roadmaps, roadmap_items, baselines (Phase 1) |
| 5 | Analytics | dashboards, chart_widgets, dashboard_shares, saved_views, report_exports |

**Hard dependency:** DEV5 Task 1 (workspaces) and DEV5 Task 2 (projects) must be complete before any DEV6 task can start.

---

## Phase 1: Base Context (Injected Into Every Worker Agent)

```
AI_CONTEXT/rules.md
AI_CONTEXT/project-context.md
AI_CONTEXT/tech-stack.md
AI_CONTEXT/known-issues.md
```

**Key concepts DEV6 must absorb:**

- `tasks.status` enum is the source of truth — `board_columns.status_key` maps to it
- Moving a card on the board = updating `tasks.status` (not just `board_task_positions`)
- `board_task_positions` stores drag-order only — card position within a column
- Sprint burndown is populated nightly by Hangfire via `sprint_daily_snapshots`
- `sprint_backlog_items` controls what's in a sprint — tasks can be added/removed mid-sprint
- Roadmaps are **Phase 1** (required by WorkSync Phase 4 user flows)
- `dashboard_shares` is a separate ACL table — `dashboards.is_shared` is just a workspace-wide quick toggle

---

## Phase 2: Task 1 — Task Management

**Task file:** `current-focus/DEV6-tasks-boards-planning.md` (Task 1 section)

**Schema files to read:**
```
database/schemas/wms-task-management.md     ← Full task schema
database/schemas/wms-project-management.md  ← projects, labels (task_tags FK target)
```

**User flows to read:**
```
Userflow/Work-Management/task-flow.md
```

**Key invariants:**
- Tasks are project-scoped (`project_id`) — never workspace-scoped directly
- Subtasks: `tasks.parent_task_id` self-FK (nullable)
- Status transitions validated server-side — not arbitrary
- Custom fields are project-level definitions; values are per-task
- `task_approvals` gates status change to `done` when approval flow is enabled on the project

---

## Phase 3: Task 2 — Boards

**Task file:** `current-focus/DEV6-tasks-boards-planning.md` (Task 2 section)

**Schema files to read:**
```
database/schemas/wms-task-management.md     ← boards, board_columns, board_task_positions
```

**Key invariants:**
- `board_columns.status_key` must map 1:1 to a valid `tasks.status` value
- Moving a card: UPDATE `tasks.status` = column.status_key, THEN UPDATE `board_task_positions`
- WIP limit enforced at application layer: count tasks in column, reject if >= wip_limit
- `board_task_positions.position` is a float or large int for insertion without reindex
- Personal boards (My Space) use `boards.project_id = null` and `boards.user_id` instead

---

## Phase 4: Task 3 — Sprint Planning

**Task file:** `current-focus/DEV6-tasks-boards-planning.md` (Task 3 section)

**Schema files to read:**
```
database/schemas/wms-planning.md            ← sprints, sprint_backlog_items, sprint_daily_snapshots, sprint_reports
```

**User flows to read:**
```
Userflow/Work-Management/planning-flow.md
```

**Key invariants:**
- Only one sprint per project can have `status = active` at a time — enforced at application layer
- `sprint_backlog_items` controls membership — NOT `tasks.sprint_id` alone
- `sprint_daily_snapshots` written nightly: one row per sprint per day, captures total/completed/remaining/added/removed story_points
- Burndown chart reads `sprint_daily_snapshots` ordered by `snapshot_date`
- Sprint complete: move incomplete items back to backlog (`sprint_backlog_items.removed_at = now()`)

---

## Phase 5: Task 4 — Roadmaps

**Task file:** `current-focus/DEV6-tasks-boards-planning.md` (Task 4 section)

**Schema files to read:**
```
database/schemas/wms-planning.md            ← roadmaps, roadmap_items, baselines
```

**Key invariants:**
- Roadmaps are **Phase 1** — required for WorkSync Phase 4 user flows (not Phase 2)
- `roadmap_items.entity_type` is polymorphic: Epic / Milestone / Sprint
- Baselines are snapshots of roadmap state at a point in time for comparison
- Roadmaps are workspace-scoped; items reference project-level epics/milestones

---

## Phase 6: Task 5 — Analytics

**Task file:** `current-focus/DEV6-tasks-boards-planning.md` (Task 5 section)

**Schema files to read:**
```
database/schemas/wms-analytics.md           ← dashboards, chart_widgets, saved_views, report_snapshots, report_exports, dashboard_shares, saved_view_shares
```

**Key invariants:**
- `dashboards.is_shared` = workspace-wide quick toggle (all members can see)
- `dashboard_shares` = fine-grained ACL (user / team / workspace, can_edit flag)
- Both must be checked when determining if a user can view a dashboard
- `report_exports` are async: Hangfire job processes, uploads to Azure Blob, sets `file_asset_id`, sends notification
- Widget `config_json` stores all filter/date-range/scope params — no separate filter tables
