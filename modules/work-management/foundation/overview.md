# Work Management Foundation

**Module:** Work Management
**Feature:** Foundation
**Namespace:** `WorkManagement.Foundation`
**Owner:** DEV3
**Tables:** 13 in schema file; foundation-owned tables are `workspaces`, `workspace_roles`, `workspace_members`, `workspace_hr_team_links`

---

## Purpose

Core workspace infrastructure for Work Management. Every Work Management entity is scoped to a workspace. Workspaces are tenant-level containers for projects, members, and roles. A tenant can have multiple workspaces.

Phase 1 workspace membership is employee-backed. `workspace_members` stores both `user_id` for auth and `employee_id` for HR joins, availability, offboarding, department/team reporting, and company tenant checks. Microsoft Teams group sync is an optional Phase 1 integration and is separate from HR team-to-workspace sync.

---

## Database Tables

### `workspaces`

Key columns: `tenant_id`, `name`, `slug`, `is_active`, `owner_id`.

### `workspace_roles`

System-seeded roles per workspace. Key columns: `workspace_id`, `name` (`Admin`, `Member`, `Viewer`), `is_system` (true for seeded roles), `permissions_json`.

On workspace creation: three rows inserted automatically (Admin, Member, Viewer).

### `workspace_members`

Join table: user to workspace plus HR employee bridge. Key columns: `workspace_id`, `user_id`, `employee_id`, `workspace_role_id`, `membership_source`, `is_active`, `invited_by_id`, `joined_at`, `removed_at`.

`employee_id` is resolved from `employees.user_id` when adding a member. Phase 1 blocks workspace membership for users without an active, non-deleted employee record.

### `workspace_hr_team_links`

Phase 1 HR team sync. Key columns: `tenant_id`, `workspace_id`, `hr_team_id`, `sync_enabled`, `last_synced_at`, `last_error`, `created_by_id`.

When enabled, changes in `team_members` add or deactivate `workspace_members` records with `membership_source = hr_team`. This is not Microsoft Teams; it is internal Org Structure team sync.

### Microsoft Teams Link Tables

`workspace_teams_links` and `teams_member_sync_status` are optional Phase 1 integration tables. They are for Microsoft Teams channel/group sync, not login, not SSO, and not the Phase 1 HR team sync bridge.

---

## Key Business Rules

1. Workspace creation seeds 3 system roles (Admin/Member/Viewer) in the same transaction.
2. If tenant has Work Management enabled, a default workspace is created on tenant provisioning.
3. Global query filters enforce both `tenant_id` and `workspace_id` on all workspace-scoped entities.
4. Active workspace carried in backend-held session metadata or `X-Workspace-Id` header; every Work Management request resolves workspace context.
5. Workspace visibility is tenant-local by default. Cross-company workspace collaboration requires an active company connection and explicit member/data-sharing scope.
6. Workspace and project members must carry `employee_id`; querying by department, team, job, company tenant, and employment status must not require application-only joins.
7. Offboarding or `employees.is_deleted = true` deactivates workspace/project memberships and prevents new task assignment.
8. HR team-to-workspace sync is Phase 1 through `workspace_hr_team_links`.
9. Microsoft Teams group creation/linking is an optional Phase 1 integration and must not be treated as SSO.

---

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `WorkspaceCreatedEvent` | New workspace created | Seeds default roles, notifies admin |
| `WorkspaceMemberAddedEvent` | User added to workspace | Notifications |
| `WorkspaceMemberRemovedEvent` | User removed | Revoke project access cascade |
| `WorkspaceHrTeamLinkedEvent` | HR team linked to workspace | Syncs team members into workspace |
| `EmployeeOffboardedEvent` | Employee is offboarded | Deactivates Work Management memberships |

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/workspaces` | `workspaces:read` | List user's workspaces |
| POST | `/api/v1/workspaces` | `workspaces:create` | Create workspace |
| GET | `/api/v1/workspaces/{id}` | `workspaces:read` | Get workspace detail |
| GET | `/api/v1/workspaces/{id}/members` | `workspaces:read` | List members |
| POST | `/api/v1/workspaces/{id}/members` | `workspaces:manage` | Invite/add employee-backed member |
| DELETE | `/api/v1/workspaces/{id}/members/{userId}` | `workspaces:manage` | Remove member |
| GET | `/api/v1/workspaces/{id}/roles` | `workspaces:read` | List workspace roles |
| GET | `/api/v1/workspaces/{id}/hr-teams` | `workspaces:manage` | List linked HR teams |
| POST | `/api/v1/workspaces/{id}/hr-teams` | `workspaces:manage` | Link HR team to workspace |
| DELETE | `/api/v1/workspaces/{id}/hr-teams/{teamId}` | `workspaces:manage` | Disable HR team sync |
| GET | `/api/v1/workspaces/{id}/teams/eligibility` | `workspaces:manage` | Check if workspace members can sync to Microsoft Teams |
| GET | `/api/v1/workspaces/{id}/teams/candidates` | `workspaces:manage` | Find existing Microsoft Teams groups with matching members |
| POST | `/api/v1/workspaces/{id}/teams/create` | `workspaces:manage` | Create a Microsoft Team for this workspace |
| POST | `/api/v1/workspaces/{id}/teams/link` | `workspaces:manage` | Link existing Microsoft Team |

---

## Related

- [[modules/work-management/overview|Work Management Module Family]]
- [[modules/work-management/projects/overview|Project Management]]
- [[modules/integrations/microsoft-teams/overview|Microsoft Teams Integration]]
- [[modules/shared-platform/company-connections/overview|Company Connections]]
- [[Userflow/Work-Management/workspace-teams-sync|Workspace Teams Sync]]
- [[database/schemas/wms-project-management|WMS Project Management Schema]]
- [[database/cross-module-relationships|Cross-Module Relationships]]
- [[current-focus/DEV3|DEV3 Task 1]]
