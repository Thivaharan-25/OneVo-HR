# Project Management

**Module:** Work Management
**Feature:** Project Management
**Namespace:** `WorkManagement.Projects`
**Owner:** DEV3
**Tables:** 8

---

## Purpose

Projects are tenant-scoped business/work containers that can involve multiple team workspaces. Tasks, sprints, boards, and roadmaps all belong to a project. Epics, milestones, and versions provide hierarchy and release planning within a project. Project membership is employee-backed so HR status, department/team reporting, and offboarding rules are enforceable.

A project is not a reporting hierarchy and is not owned by exactly one workspace. The owning legal entity is inferred from the creator's active legal entity context at creation time. Cross-legal-entity or cross-workspace participation requires a participation request and approval from the target workspace/legal-entity authority. Approval grants project collaboration only; it does not grant reporting authority over the target entity's employees.

---

## Database Tables

### `projects`

Key columns: `tenant_id`, `owning_legal_entity_id`, `name`, `description`, `status` (`active`, `archived`, `completed`), `lead_id`, `start_date`, `target_date`.

`owning_legal_entity_id` is set from the active legal entity context. Users with access to multiple legal entities choose the context before opening Create Project. Normal project creation does not expose owning legal entity as a free-form field.

### `project_workspaces`

Key columns: `project_id`, `workspace_id`, `tenant_id`, `legal_entity_id`, `status` (`pending`, `approved`, `active`, `rejected`, `removed`), `requested_by_id`, `approved_by_id`, `linked_by_id`, `linked_at`, `is_active`.

This table records which workspaces are involved in a project. It is context only; it does not grant project access to every member of those workspaces. If the requester controls both the project and the workspace, the link can become active immediately. Otherwise the row starts as `pending` and becomes active only after workspace/legal-entity approval.

### `project_members`

Key columns: `project_id`, `user_id`, `employee_id`, `role` (`Admin`, `Member`, `Viewer`), `membership_source`, `is_active`, `added_by_id`, `added_at`, `removed_at`.

Project `admin` is local to that project. Workspace Admin does not implicitly have full project access unless they are also a project member or a tenant security role explicitly allows project administration inside the relevant scope.

Project membership is the source of truth for project visibility. A linked workspace is a source pool and reporting context; it is not automatic project visibility for every workspace member unless a project policy explicitly adds selected members.

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
2. Project owning legal entity is inferred from active legal entity context during creation.
3. `project.identifier` is immutable after first task is created; changing it would break all task references.
4. Labels are project-scoped by default; tenant-wide reusable labels are allowed only when `project_id` is null.
5. Epics span the project lifecycle; milestones are date-targeted checkpoints.
6. A project must have at least one active `admin` project member at all times.
7. Adding a project member requires an active, non-deleted `employees` row or an approved connected-company participant projection. It does not require full workspace membership.
8. Employee offboarding deactivates project membership; historical assignments remain auditable.
9. Linking a workspace to a project does not make every workspace member a project member.
10. A workspace outside the creator's managed context requires a participation request. The target workspace/legal-entity approver can approve, reject, or limit the requested members/data visibility.
11. Task progress and health roll up by responsible workspace and legal entity from task ownership, not from reporting hierarchy alone.

## User Journey: Multi-Workspace Project

1. User opens Projects in the active legal entity context and clicks Create Project.
2. System creates the project with `owning_legal_entity_id` from the active legal entity and adds the creator as a local project admin.
3. User adds a workspace:
   - If the user manages that workspace, the link is active immediately.
   - If the workspace is outside the user's managed context, the system creates a pending participation request.
4. The target workspace/legal-entity approver reviews the request, including requested project purpose, member/data visibility, and expected task responsibility.
5. On approval, `project_workspaces.status` becomes `active`.
6. Project admin selects project members from approved workspaces, direct invites, or approved connected-company projections.
7. Tasks are created with `project_id` and responsible `workspace_id`.
8. Project dashboards roll up progress and health by workspace, legal entity, milestone, and task status.

## Visibility Journey

When a user opens a project:

1. System verifies `projects:read` and active project membership or a scoped approved participation grant.
2. System determines the viewer context: project administration, legal-entity context, workspace context, reporting-manager context, project member, or viewer/stakeholder.
3. The dashboard is filtered:
   - Full project administration context sees all project health and all participation.
   - Legal-entity context sees only that entity's contribution and approvals.
   - Workspace context sees only that workspace's contribution.
   - Reporting managers see only their reports' work inside project/workspace contexts they can access.
   - Members see own/watch/assigned work and published announcements.
4. Sensitive risks, blockers, workload, and approval queues are hidden unless the viewer context allows them.

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
