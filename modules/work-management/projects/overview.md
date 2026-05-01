# Project Management

**Module:** WorkSync
**Feature:** Project Management
**Namespace:** `WorkSync.Projects`
**Owner:** DEV5
**Tables:** 7

---

## Purpose

Projects are the primary organisational unit within a workspace. Tasks, sprints, boards, and roadmaps all belong to a project. Epics, milestones, and versions provide hierarchy and release planning within a project.

---

## Database Tables

### `projects`
Key columns: `workspace_id`, `tenant_id`, `name`, `slug`, `description`, `status` (`active`, `archived`, `on_hold`), `start_date`, `end_date`, `owner_id`, `identifier` (short prefix e.g. `TASK` → `TASK-123`).

### `project_members`
Key columns: `project_id`, `user_id`, `role` (`Owner`, `Admin`, `Member`, `Viewer`), `added_by_id`, `added_at`.

Owner role is always exactly one user. Workspace Admin implicitly has full project access.

### `epics`
Key columns: `project_id`, `workspace_id`, `tenant_id`, `title`, `description`, `status`, `start_date`, `end_date`, `owner_id`, `color`.

Tasks reference epics via `tasks.epic_id`.

### `milestones`
Key columns: `project_id`, `title`, `due_date`, `status` (`upcoming`, `reached`, `missed`), `description`.

### `versions`
Key columns: `project_id`, `name`, `description`, `start_date`, `release_date`, `status` (`unreleased`, `released`, `archived`).

Tasks can be assigned to a version via `tasks.version_id`.

### `release_calendar`
Key columns: `project_id`, `version_id`, `scheduled_date`, `release_type` (`major`, `minor`, `patch`), `notes`.

### `labels`
Key columns: `workspace_id` (workspace-scoped, not project-scoped — reusable across projects), `name`, `color`, `description`.

Tasks reference labels via `task_tags.label_id`.

---

## Key Business Rules

1. Projects are workspace-scoped — `project_id` always implies `workspace_id`.
2. `project.identifier` is immutable after first task is created — changing it would break all task references.
3. Labels are workspace-scoped: one label can appear in multiple projects.
4. Epics span the project lifecycle; milestones are date-targeted checkpoints.
5. Project must have exactly one Owner role member at all times.

---

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `ProjectCreatedEvent` | Project created | Notifications (notify invitees) |
| `ProjectArchivedEvent` | Project status → archived | Close open sprints, notify members |
| `MilestoneReachedEvent` | Milestone status → reached | Notifications |

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/workspaces/{wsId}/projects` | `projects:read` | List workspace projects |
| POST | `/api/v1/workspaces/{wsId}/projects` | `projects:create` | Create project |
| GET | `/api/v1/projects/{id}` | `projects:read` | Get project |
| PATCH | `/api/v1/projects/{id}` | `projects:write` | Update project |
| GET | `/api/v1/projects/{id}/members` | `projects:read` | List project members |
| POST | `/api/v1/projects/{id}/members` | `projects:write` | Add member |
| GET | `/api/v1/projects/{id}/epics` | `projects:read` | List epics |
| POST | `/api/v1/projects/{id}/epics` | `projects:write` | Create epic |
| GET | `/api/v1/projects/{id}/milestones` | `projects:read` | List milestones |
| GET | `/api/v1/projects/{id}/versions` | `projects:read` | List versions |
| GET | `/api/v1/workspaces/{wsId}/labels` | `projects:read` | List workspace labels |

---

## Related

- [[modules/work-management/foundation/overview|Foundation]]
- [[modules/work-management/tasks/overview|Task Management]]
- [[modules/work-management/planning/overview|Planning (Sprints + Boards)]]
- [[database/schemas/wms-project-management|WMS Project Management Schema]]
- [[current-focus/DEV5-wms-foundation|DEV5 Task 2]]
