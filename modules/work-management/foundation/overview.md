# Work Management Foundation

**Module:** Work Management
**Feature:** Foundation
**Namespace:** `WorkManagement.Foundation`
**Owner:** DEV3

---

## Purpose



Workspace membership can be created from direct member invitations:

- **Manual Invite**: employee/member search filtered by the actor's active Company context and member-management authority. Selected members receive an invite and accept or decline.

Workspace authority applies only inside that workspace. Reporting-manager relationship does not grant workspace or project authority; the actor must have the relevant local workspace/project authority.

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




### Microsoft Teams Link Tables

`workspace_teams_links` and `teams_member_sync_status` are optional Phase 2 integration tables for Microsoft Teams workspace/group sync. They are not login, SSO, Org Structure reporting views, or project membership.

---

## Key Business Rules

1. Workspace creation seeds 3 system roles (Admin/Member/Viewer) in the same transaction.
2. If tenant has Work Management enabled, a default workspace is created on tenant provisioning.
3. Global query filters enforce `tenant_id` on all Work Management entities and `workspace_id` on workspace-scoped entities.
5. Workspace visibility is tenant-local by default. Cross-company workspace collaboration requires an active company connection and explicit member/data-sharing scope.
7. Offboarding or `employees.is_deleted = true` deactivates `workspace_members` and `project_members` access and prevents new task assignment.
9. Microsoft Teams group creation/linking is an optional Phase 2 integration unless explicitly reactivated and must not be treated as SSO.
11. Workspace member search must be filtered by the actor's active Company context and member-management authority. Phase 1 does not use linked workspace source pools or owner-to-owner participation requests.
12. Creating a project from a workspace requires project creation permission plus workspace authority. The created project stores that workspace as its single `workspace_id`; future project access is still controlled by `project_members`.


1. User opens Work -> Workspaces -> Create Workspace.
2. System checks `workspaces:create` and resolves the active legal entity context.
4. UI lets the user invite eligible employees/members and choose workspace roles.
5. On save, system creates the workspace and sends direct member invitations where members were selected.
6. Accepted invitations create `workspace_members`.

## User Journey: Invite Workspace Member

1. Workspace authority holder opens Workspace Settings -> Members -> Invite.
2. Search is filtered by active Company context and the actor's member-management authority.
3. The selected member receives a direct invitation.
4. On acceptance, the employee-backed user is added as a workspace member with the selected local role.

---

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `WorkspaceCreatedEvent` | New workspace created | Seeds default roles, notifies admin |
| `WorkspaceMemberAddedEvent` | User added to workspace | Notifications |
| `WorkspaceMemberRemovedEvent` | User removed | Re-evaluate workspace-scoped access; do not remove project membership unless a project policy explicitly depends on that workspace membership |
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
| GET | `/api/v1/workspaces/{id}/teams/eligibility` | `workspaces:manage` | Phase 2: check if workspace members can sync to Microsoft Teams |
| GET | `/api/v1/workspaces/{id}/teams/candidates` | `workspaces:manage` | Phase 2: find existing Microsoft Teams groups with matching members |

---

## Related

- [[modules/work-management/overview|Work Management Module Family]]
- [[modules/work-management/projects/overview|Project Management]]
- [[modules/integrations/microsoft-teams/overview|Microsoft Teams Integration]]
- [[modules/shared-platform/company-connections/overview|Company Connections]]
- [[database/schemas/wms-project-management|WMS Project Management Schema]]
- [[database/cross-module-relationships|Cross-Module Relationships]]
- [[current-focus/DEV3|DEV3 Task 1]]
