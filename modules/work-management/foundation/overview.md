# Work Management Foundation

**Module:** Work Management
**Feature:** Foundation
**Namespace:** `WorkManagement.Foundation`
**Owner:** DEV3
**Tables:** 13 in schema file; foundation-owned tables are `workspaces`, `workspace_roles`, `workspace_members`, `workspace_team_links`

---

## Purpose

Core workspace infrastructure for Work Management. Workspaces are team/work-area containers for workspace members, chat, workspace-level resources, and integration context. A tenant can have multiple workspaces. Projects are tenant-scoped and can link to multiple workspaces through `project_workspaces`; a project is not owned by exactly one workspace.

Phase 1 workspace membership is employee-backed. `workspace_members` stores both `user_id` for auth and `employee_id` for HR joins, availability, offboarding, department/team reporting, and company tenant checks. Microsoft Teams group sync is an optional Phase 1 integration and is separate from explicit Org Structure team-to-workspace sync.

Workspace membership can be created from three source types:

- **My Reporting Team**: virtual source resolved from position hierarchy. It does not create or require a stored Org Structure team.
- **Existing Explicit Team**: stored Org Structure team linked through `workspace_team_links`.
- **Manual Invite**: employee search filtered by hierarchy, bypass grants, organization-wide authority, or invite approval.

Workspace authority applies only inside that workspace. A reporting manager's hierarchy authority does not automatically transfer into another manager's workspace unless they are granted the relevant workspace/project authority there.

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

### `workspace_team_links`

Phase 1 explicit team sync. Key columns: `tenant_id`, `workspace_id`, `team_id`, `sync_enabled`, `last_synced_at`, `last_error`, `created_by_id`.

When enabled, changes in `team_members` add or deactivate `workspace_members` records with `membership_source = team_sync`. This is not Microsoft Teams; it is internal Org Structure team sync.

### Microsoft Teams Link Tables

`workspace_teams_links` and `teams_member_sync_status` are optional Phase 1 integration tables. They are for Microsoft Teams channel/group sync, not login, not SSO, and not the Phase 1 explicit team sync bridge.

---

## Key Business Rules

1. Workspace creation seeds 3 system roles (Admin/Member/Viewer) in the same transaction.
2. If tenant has Work Management enabled, a default workspace is created on tenant provisioning.
3. Global query filters enforce `tenant_id` on all Work Management entities and `workspace_id` on workspace-scoped entities.
4. Active workspace can be carried in backend-held session metadata or `X-Workspace-Id` header for workspace-scoped screens. Project-scoped requests resolve access from `project_members` and use `project_workspaces` only as workspace/team context.
5. Workspace visibility is tenant-local by default. Cross-company workspace collaboration requires an active company connection and explicit member/data-sharing scope.
6. Workspace members and project members must carry `employee_id`; querying by department, team, job, company tenant, and employment status must not require application-only joins.
7. Offboarding or `employees.is_deleted = true` deactivates `workspace_members` and `project_members` access and prevents new task assignment.
8. Explicit team-to-workspace sync is Phase 1 through `workspace_team_links`.
9. Microsoft Teams group creation/linking is an optional Phase 1 integration and must not be treated as SSO.
10. Creating a workspace from "My Reporting Team" inserts `workspace_members` only. It must not insert a duplicate `teams` row.
11. Workspace member search must be filtered by the actor's allowed member pool. For scoped managers this is their position-derived reporting hierarchy; for broader admins it is their authorized legal entity/tenant scope; for outside members it is an invite/approval flow.
12. Creating a project from a workspace requires project creation permission plus workspace authority. The created project is auto-linked to the workspace through `project_workspaces`, but future project access is still controlled by `project_members`.

## User Journey: Create Workspace From Reporting Team

1. User opens WorkSync -> Workspaces -> Create Workspace.
2. System checks `workspaces:create` and resolves the active legal entity context.
3. User chooses member source: "My Reporting Team".
4. Backend resolves eligible members from `employee_hierarchy_closure` for the creator's employee id.
5. UI shows only eligible employees and lets the user choose workspace roles.
6. On save, system creates the workspace and `workspace_members`.
7. No `teams` or `team_members` records are created.

## User Journey: Add External Workspace Member

1. Workspace authority holder opens Workspace Settings -> Members -> Invite.
2. Search defaults to employees inside the actor's allowed hierarchy/legal-entity scope.
3. If the user searches outside that pool, the UI offers "Request participation" instead of direct add.
4. The target employee's manager, workspace owner, legal-entity approver, or configured resolver receives the request.
5. On approval, the employee is added as a workspace member with the selected local role.

---

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `WorkspaceCreatedEvent` | New workspace created | Seeds default roles, notifies admin |
| `WorkspaceMemberAddedEvent` | User added to workspace | Notifications |
| `WorkspaceMemberRemovedEvent` | User removed | Re-evaluate workspace-scoped access; do not remove project membership unless a project policy explicitly depends on that workspace membership |
| `WorkspaceTeamLinkedEvent` | Explicit team linked to workspace | Syncs team members into workspace |
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
| GET | `/api/v1/workspaces/{id}/org-teams` | `workspaces:manage` | List linked explicit Org Structure teams |
| POST | `/api/v1/workspaces/{id}/org-teams` | `workspaces:manage` | Link explicit Org Structure team to workspace |
| DELETE | `/api/v1/workspaces/{id}/org-teams/{teamId}` | `workspaces:manage` | Disable explicit team sync |
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
