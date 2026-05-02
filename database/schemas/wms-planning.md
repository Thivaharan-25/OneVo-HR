# Schema: Work Management - Planning

**Module:** `Work Management.Planning`
**Phase:** 1 (including roadmaps - Phase 1 for Work Management)
**Owner:** DEV3

---

## `sprints` - Phase 1

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `project_id` | uuid | FK -> projects |
| `name` | varchar(100) | |
| `goal` | text | nullable |
| `start_date` | date | |
| `end_date` | date | |
| `status` | varchar(20) | planned / active / completed |
| `created_at` | timestamptz | |
| `updated_at` | timestamptz | |

**Constraint:** At most one sprint per project with `status = active` (partial unique index)
**Index:** `(project_id, status)`

---

## `sprint_backlog_items` - Phase 1

Snapshot of tasks committed to a sprint. Decoupled from `board_task_positions` so board column can differ from backlog commitment.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `sprint_id` | uuid | FK -> sprints |
| `task_id` | uuid | FK -> tasks |
| `story_points` | int | nullable; locked at sprint start |
| `added_at` | timestamptz | |
| `added_by_id` | uuid | FK -> users |

**Unique:** `(sprint_id, task_id)`

**Rule:** Sprint planning must surface assignment availability warnings from `task_assignments.availability_status` before committing sprint scope.

---

## `sprint_daily_snapshots` - Phase 1

One row per sprint per calendar day. Powers burndown charts.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `sprint_id` | uuid | FK -> sprints |
| `snapshot_date` | date | |
| `total_points` | int | All committed story points |
| `completed_points` | int | Story points of tasks in done status |
| `remaining_points` | int | total_points - completed_points |
| `added_points` | int | Scope creep; points added after sprint start |
| `removed_points` | int | Points removed from sprint after start |

**Unique:** `(sprint_id, snapshot_date)`

**Hangfire job:** Runs daily at 23:59 tenant timezone. Scans all active sprints and inserts snapshot row.

---

## `sprint_reports` - Phase 1

One row per completed sprint. Post-mortem summary.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `sprint_id` | uuid | FK -> sprints, UNIQUE |
| `velocity` | numeric(8,2) | Completed story points |
| `completed_points` | int | |
| `incomplete_points` | int | Points carried to next sprint |
| `summary_json` | jsonb | Task counts by status and textual summary only; contributor metrics live in `sprint_report_contributors` |
| `created_at` | timestamptz | Created on sprint complete |

---

## `sprint_report_contributors` - Phase 1

Typed contributor rows for completed sprint reports. This keeps contributor data queryable by HR dimensions such as department, job title, and employment status.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `sprint_report_id` | uuid | FK -> sprint_reports |
| `user_id` | uuid | FK -> users |
| `employee_id` | uuid | FK -> employees |
| `completed_task_count` | int | |
| `completed_story_points` | int | |
| `review_count` | int | nullable |
| `rank` | int | Display order in report |

**Unique:** `(sprint_report_id, user_id)`
**Index:** `(employee_id)`, `(sprint_report_id, rank)`

---

## `roadmaps` - Phase 1 (for Work Management)

> Originally marked Phase 2 in the HR phase plan, but promoted to Phase 1 because the Work Management user flow requires roadmap functionality.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `workspace_id` | uuid | FK -> workspaces |
| `name` | varchar(100) | |
| `start_date` | date | nullable |
| `end_date` | date | nullable |
| `is_shared` | boolean | default true; visible to all workspace members |
| `created_by_id` | uuid | FK -> users |
| `created_at` | timestamptz | |
| `updated_at` | timestamptz | |

---

## `roadmap_items` - Phase 1 (for Work Management)

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `roadmap_id` | uuid | FK -> roadmaps |
| `entity_type` | varchar(30) | Epic / Milestone / Sprint / Version |
| `entity_id` | uuid | Polymorphic FK to epics/milestones/sprints/versions |
| `position` | int | Left-to-right order on timeline |
| `color` | varchar(20) | nullable; override entity color |

---

## `baselines` - Phase 1

Point-in-time snapshot of a project plan for comparison.

| Column | Type | Notes |
|---|---|---|
| `id` | uuid | PK |
| `project_id` | uuid | FK -> projects |
| `name` | varchar(100) | |
| `snapshot_json` | jsonb | Task list + sprint assignments + dates at snapshot time |
| `created_by_id` | uuid | FK -> users |
| `created_at` | timestamptz | |
