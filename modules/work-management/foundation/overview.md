# WorkSync Foundation

**Module:** WorkSync
**Feature:** Foundation
**Namespace:** `WorkSync.Foundation`
**Owner:** DEV5
**Tables:** 5

---

## Purpose

Core workspace infrastructure for WorkSync. Every WorkSync entity is scoped to a workspace. Workspaces are tenant-level containers for projects, members, and roles. A tenant can have multiple workspaces.

Workspace creation can optionally create or link a Microsoft Teams group when the tenant has Teams sync enabled. The Graph integration is owned by [[modules/integrations/microsoft-teams/overview|Microsoft Teams Integration]].

---

## Database Tables

### `workspaces`
Key columns: `tenant_id`, `legal_entity_id` (nullable — binds WMS visibility to HR entity), `name`, `slug`, `is_active`, `created_by_id`.

### `workspace_roles`
Teams mapping is stored in `workspace_teams_links`; do not store Graph IDs directly on `workspaces`.

System-seeded roles per workspace. Key columns: `workspace_id`, `name` (`Admin`, `Member`, `Viewer`), `is_system` (true for seeded roles), `permissions_json`.

On workspace creation: three rows inserted automatically (Admin, Member, Viewer).

### `workspace_members`
Join table: user ↔ workspace. Key columns: `workspace_id`, `user_id`, `workspace_role_id`, `invited_by_id`, `joined_at`.

Employees are linked via `employees.user_id = workspace_members.user_id`.

---

## Key Business Rules

1. Workspace creation seeds 3 system roles (Admin/Member/Viewer) in the same transaction.
2. If tenant has WorkSync enabled, a default workspace is created on tenant provisioning.
3. Global query filters enforce BOTH `tenant_id` AND `workspace_id` on all workspace-scoped entities.
4. Active workspace carried in JWT claims or `X-Workspace-Id` header — every WorkSync request resolves workspace context.
5. Workspace bound to a `legal_entity_id`: WMS visibility respects HR topbar legal entity scope when set.
6. Teams group creation is optional during workspace creation and must be explicitly selected by checkbox.
7. Existing Teams group sync requires member matching and admin confirmation before linking.
8. A workspace can have at most one active Microsoft Teams link at a time.

---

## Domain Events

| Event | Published When | Consumers |
|:------|:---------------|:----------|
| `WorkspaceCreatedEvent` | New workspace created | Seeds default roles, notifies admin |
| `WorkspaceMemberAddedEvent` | User added to workspace | Notifications |
| `WorkspaceMemberRemovedEvent` | User removed | Revoke project access cascade |

---

## API Endpoints

| Method | Route | Permission | Description |
|:-------|:------|:-----------|:------------|
| GET | `/api/v1/workspaces` | `workspaces:read` | List user's workspaces |
| POST | `/api/v1/workspaces` | `workspaces:create` | Create workspace |
| GET | `/api/v1/workspaces/{id}` | `workspaces:read` | Get workspace detail |
| GET | `/api/v1/workspaces/{id}/members` | `workspaces:read` | List members |
| POST | `/api/v1/workspaces/{id}/members` | `workspaces:manage` | Invite member |
| DELETE | `/api/v1/workspaces/{id}/members/{userId}` | `workspaces:manage` | Remove member |
| GET | `/api/v1/workspaces/{id}/roles` | `workspaces:read` | List workspace roles |
| GET | `/api/v1/workspaces/{id}/teams/eligibility` | `workspaces:manage` | Check if workspace members can sync to Teams |
| GET | `/api/v1/workspaces/{id}/teams/candidates` | `workspaces:manage` | Find existing Teams groups with matching members |
| POST | `/api/v1/workspaces/{id}/teams/create` | `workspaces:manage` | Create a Microsoft Team for this workspace |
| POST | `/api/v1/workspaces/{id}/teams/link` | `workspaces:manage` | Link existing Microsoft Team |

---

## Related

- [[modules/work-management/overview|WorkSync Module Family]]
- [[modules/work-management/projects/overview|Project Management]]
- [[modules/integrations/microsoft-teams/overview|Microsoft Teams Integration]]
- [[Userflow/Work-Management/workspace-teams-sync|Workspace Teams Sync]]
- [[database/schemas/wms-project-management|WMS Project Management Schema]]
- [[current-focus/DEV5-wms-foundation|DEV5 Task 1]]
