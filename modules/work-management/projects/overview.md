# Project Management

**Module:** Work Management
**Feature:** Project Management
**Namespace:** `WorkManagement.Projects`
**Owner:** DEV3
**Tables:** 8

---

## Purpose


Phase 1 Project Management is intentionally simple: projects, one owning workspace per project, work items, project member invitations, project members, simple project-link invitations, project settings, labels, and lightweight milestones where retained. A project is not a reporting hierarchy. The owning legal entity is inferred from the creator's active legal entity context at creation time and is not exposed as a free-form creation field.

Older workspace-heavy collaboration, workspace source pools, and cross-workspace participation rules are Phase 2 design references. They must not be treated as active Phase 1 project behavior unless a later product decision explicitly reactivates them.

---

## Database Tables

### `projects`

Key columns: `tenant_id`, `owning_legal_entity_id`, `workspace_id`, `name`, `description`, `status` (`active`, `archived`, `completed`), `lead_id`, `start_date`, `target_date`.

`owning_legal_entity_id` is set from the active legal entity context. `workspace_id` is set from the selected workspace context. Users with access to multiple legal entities choose the Company context before opening Create Project. Normal project creation does not expose owning legal entity as a free-form field.

### `project_workspaces` - Phase 2 Reference

Key columns: `project_id`, `workspace_id`, `tenant_id`, `legal_entity_id`, `status` (`pending`, `approved`, `active`, `rejected`, `removed`), `requested_by_id`, `approved_by_id`, `linked_by_id`, `linked_at`, `is_active`.

Phase 2 reference only. Phase 1 projects store one `projects.workspace_id`; project access comes from `project_members` and scoped project permissions, not workspace participation requests.

### `project_member_invitations`

Key columns: `project_id`, `tenant_id`, `invited_user_id`, `invited_employee_id`, `role`, `status` (`pending`, `accepted`, `declined`, `expired`, `cancelled`), `invited_by_id`, `decided_at`, `expires_at`.

Project/workspace admins invite selected members directly. The selected member must accept before the active `project_members` row is created.

### `project_link_invitations`

Key columns: `source_project_id`, `target_project_id`, `tenant_id`, `invited_project_admin_id`, `status` (`pending`, `accepted`, `declined`, `expired`, `cancelled`), `invited_by_id`, `decided_at`, `expires_at`.

Phase 1 allows simple project-link invitations between project admins. This is not an advanced dependency platform.

### `project_links`

Key columns: `source_project_id`, `target_project_id`, `tenant_id`, `link_type`, `created_by_id`, `created_at`, `is_active`.

Created only after a project-link invitation is accepted.

### `project_members`

Key columns: `project_id`, `user_id`, `employee_id`, `role` (`Admin`, `Member`, `Viewer`), `membership_source`, `is_active`, `added_by_id`, `added_at`, `removed_at`.

Project `admin` is local to that project. Workspace Admin does not implicitly have full project access unless they are also a project member or a tenant security role explicitly allows project administration inside the relevant scope.

Project membership is the Phase 1 source of truth for project visibility.

### `epics` - Phase 2 Reference

Key columns: `project_id`, `tenant_id`, `title`, `description`, `status`, `start_date`, `end_date`, `owner_id`, `color`.

Advanced project hierarchy. Phase 1 tasks may keep nullable compatibility fields, but Phase 1 screens must not require epics.

### `milestones`

Key columns: `project_id`, `title`, `due_date`, `status` (`upcoming`, `reached`, `missed`), `description`.

### `versions` - Phase 2 Reference

Key columns: `project_id`, `name`, `description`, `start_date`, `release_date`, `status` (`unreleased`, `released`, `archived`).

Release/version planning is Phase 2 unless explicitly reactivated.

### `release_calendar` - Phase 2 Reference

Key columns: `project_id`, `version_id`, `scheduled_date`, `release_type` (`major`, `minor`, `patch`), `notes`.

### `labels`

Key columns: `tenant_id`, `project_id` (nullable for tenant-wide reusable labels), `name`, `color`, `description`.

Tasks reference labels via `task_tags.label_id`.

---

## Key Business Rules

1. Projects are tenant-scoped and use direct accepted project membership for Phase 1 visibility.
2. Project owning legal entity is inferred from active legal entity context during creation.
3. Each Phase 1 project belongs to exactly one workspace through `projects.workspace_id`.
4. `project.identifier` is immutable after first task is created; changing it would break all task references.
5. Labels are project-scoped by default; tenant-wide reusable labels are allowed only when `project_id` is null.
6. Milestones are date-targeted checkpoints where retained; epics, versions, and release calendars are Phase 2 planning references.
7. A project must have at least one active `admin` project member at all times.
8. Adding a project member requires a pending invitation to an active, non-deleted `employees` row in the tenant and acceptance by the selected member.
9. Employee offboarding deactivates project membership; historical assignments remain auditable.
10. Workspace participation requests, connected-company participant projections, workspace source pools, and workspace/legal-entity project contribution rollups are Phase 2 references.
11. Simple Phase 1 project health is based on task status, due dates, project members, and retained milestones.
12. Simple Phase 1 project links are accepted relationship records between projects; advanced project-linking/dependency management is Phase 2.

## User Journey: Phase 1 Project

1. User opens Projects in the active legal entity context and clicks Create Project.
2. System creates the project with `owning_legal_entity_id` from the active legal entity, `workspace_id` from the selected workspace, and adds the creator as a local project admin.
3. Project admin invites active employee-backed members.
4. Invited members accept or decline.
5. Accepted members create work items under the project and use Kanban, List, or Calendar views.
6. Project summary shows simple progress from task status, due dates, member assignments, and retained milestones.

## Visibility Journey

When a user opens a project:

1. System verifies `projects:read`.
2. System verifies active project membership or a scoped tenant/project permission.
3. Project admins see project settings, members, and all work items in the project.
4. Members see assigned, watched, and visible project work.
5. Broader workspace, legal-entity, and cross-company contribution views are Phase 2 references.

---

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `ProjectCreatedEvent` | Project created | Notifications (notify invitees) |
| `ProjectMemberAddedEvent` | Employee-backed member added | Notifications |
| `ProjectMemberRemovedEvent` | Member removed or offboarded | Revoke project access |
| `ProjectArchivedEvent` | Project status -> archived | Notify project members and stop new Phase 1 work item creation |
| `MilestoneReachedEvent` | Milestone status -> reached | Notifications |

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/projects` | `projects:read` | List projects visible to current user via `project_members` |
| POST | `/api/v1/projects` | `projects:create` | Create project |
| GET | `/api/v1/projects/{id}` | `projects:read` | Get project |
| PATCH | `/api/v1/projects/{id}` | `projects:write` | Update project |
| GET | `/api/v1/projects/{id}/workspaces` | `projects:read` | Phase 2: list linked workspaces |
| POST | `/api/v1/projects/{id}/workspaces` | `projects:write` | Phase 2: link workspace to project |
| DELETE | `/api/v1/projects/{id}/workspaces/{workspaceId}` | `projects:write` | Phase 2: unlink workspace from project |
| GET | `/api/v1/projects/{id}/members` | `projects:read` | List project members |
| POST | `/api/v1/projects/{id}/member-invitations` | `projects:write` | Invite employee-backed member |
| POST | `/api/v1/projects/{id}/member-invitations/{inviteId}/decision` | authenticated invite recipient | Accept or decline project member invitation |
| GET | `/api/v1/projects/{id}/links` | `projects:read` | List accepted simple project links |
| POST | `/api/v1/projects/{id}/link-invitations` | `projects:write` | Invite another project admin to create a simple project link |
| POST | `/api/v1/projects/{id}/link-invitations/{inviteId}/decision` | authenticated target project admin | Accept or decline project-link invitation |
| GET | `/api/v1/projects/{id}/epics` | `projects:read` | Phase 2: list epics |
| POST | `/api/v1/projects/{id}/epics` | `projects:write` | Phase 2: create epic |
| GET | `/api/v1/projects/{id}/milestones` | `projects:read` | List milestones |
| GET | `/api/v1/projects/{id}/versions` | `projects:read` | Phase 2: list versions |
| GET | `/api/v1/projects/{id}/labels` | `projects:read` | List project labels |

---

## Related

- [[modules/work-management/foundation/overview|Foundation]]
- [[modules/work-management/tasks/overview|Task Management]]
- [[modules/work-management/planning/overview|Planning (Sprints + Boards) - Phase 2]]
- [[database/schemas/wms-project-management|WMS Project Management Schema]]
- [[database/cross-module-relationships|Cross-Module Relationships]]
- [[current-focus/DEV3|DEV3 Task 1]]
