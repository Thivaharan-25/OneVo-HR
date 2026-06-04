# Project Management

**Module:** Work Management
**Feature:** Project Management
**Namespace:** `WorkManagement.Projects`
**Owner:** DEV3
**Tables:** 8

---

## Purpose

Projects are tenant-scoped business/work containers that can involve multiple team workspaces. Tasks, sprints, boards, and roadmaps all belong to a project. Epics, milestones, and versions provide hierarchy and release planning within a project. Project membership is employee-backed so HR status, department/team reporting, and offboarding rules are enforceable.

---

## Database Tables

### `projects`

Key columns: `tenant_id`, `name`, `description`, `status` (`active`, `archived`, `completed`), `lead_id`, `start_date`, `target_date`.

### `project_workspaces`

Key columns: `project_id`, `workspace_id`, `tenant_id`, `linked_by_id`, `linked_at`, `is_active`.

This table records which team workspaces are involved in a project. It is context only; it does not grant project access to every member of those workspaces.

### `project_members`

Key columns: `project_id`, `user_id`, `employee_id`, `role` (`Admin`, `Member`, `Viewer`), `membership_source`, `is_active`, `added_by_id`, `added_at`, `removed_at`.

Project `admin` is local to that project. Workspace Admin does not implicitly have full project access unless they are also a project member or a tenant security role explicitly allows project administration inside the relevant scope.

### `epics`

Key columns: `project_id`, `tenant_id`, `title`, `description`, `status`, `start_date`, `end_date`, `owner_id`, `color`.

Tasks reference epics via `tasks.epic_id`.

### `milestones`

Key columns: `project_id`, `title`, `due_date`, `status` (`upcoming`, `reached`, `missed`), `description`.

### `versions`

Key columns: `project_id`, `name`, `description`, `start_date`, `release_date`, `status` (`unreleased`, `released`, `archived`).

Tasks can be assigned to a version via `tasks.version_id`.

### `release_calendar`

Key columns: `project_id`, `version_id`, `scheduled_date`, `release_type` (`major`, `minor`, `patch`), `notes`.

### `labels`

Key columns: `tenant_id`, `project_id` (nullable for tenant-wide reusable labels), `name`, `color`, `description`.

Tasks reference labels via `task_tags.label_id`.

---

## Key Business Rules

1. Projects are tenant-scoped and can link to multiple workspaces through `project_workspaces`; `project_id` does not imply one workspace.
2. `project.identifier` is immutable after first task is created; changing it would break all task references.
3. Labels are project-scoped by default; tenant-wide reusable labels are allowed only when `project_id` is null.
4. Epics span the project lifecycle; milestones are date-targeted checkpoints.
5. A project must have at least one active `admin` project member at all times.
6. Adding a project member requires an active, non-deleted `employees` row. It does not require full workspace membership.
7. Employee offboarding deactivates project membership; historical assignments remain auditable.
8. Linking a workspace to a project does not make every workspace member a project member.

---

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `ProjectCreatedEvent` | Project created | Notifications (notify invitees) |
| `ProjectMemberAddedEvent` | Employee-backed member added | Notifications |
| `ProjectMemberRemovedEvent` | Member removed or offboarded | Revoke project access |
| `ProjectArchivedEvent` | Project status -> archived | Close open sprints, notify members |
| `MilestoneReachedEvent` | Milestone status -> reached | Notifications |

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/projects` | `projects:read` | List projects visible to current user via `project_members` |
| POST | `/api/v1/projects` | `projects:create` | Create project |
| GET | `/api/v1/projects/{id}` | `projects:read` | Get project |
| PATCH | `/api/v1/projects/{id}` | `projects:write` | Update project |
| GET | `/api/v1/projects/{id}/workspaces` | `projects:read` | List linked workspaces |
| POST | `/api/v1/projects/{id}/workspaces` | `projects:write` | Link workspace to project |
| DELETE | `/api/v1/projects/{id}/workspaces/{workspaceId}` | `projects:write` | Unlink workspace from project |
| GET | `/api/v1/projects/{id}/members` | `projects:read` | List project members |
| POST | `/api/v1/projects/{id}/members` | `projects:write` | Add employee-backed member |
| GET | `/api/v1/projects/{id}/epics` | `projects:read` | List epics |
| POST | `/api/v1/projects/{id}/epics` | `projects:write` | Create epic |
| GET | `/api/v1/projects/{id}/milestones` | `projects:read` | List milestones |
| GET | `/api/v1/projects/{id}/versions` | `projects:read` | List versions |
| GET | `/api/v1/projects/{id}/labels` | `projects:read` | List project labels |

---

## Related

- [[modules/work-management/foundation/overview|Foundation]]
- [[modules/work-management/tasks/overview|Task Management]]
- [[modules/work-management/planning/overview|Planning (Sprints + Boards)]]
- [[database/schemas/wms-project-management|WMS Project Management Schema]]
- [[database/cross-module-relationships|Cross-Module Relationships]]
- [[current-focus/DEV3|DEV3 Task 1]]
