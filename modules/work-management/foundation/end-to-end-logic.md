# WorkSync Foundation — End-to-End Logic

**Module:** WorkSync
**Feature:** Foundation

---

## Create Workspace

```
POST /api/v1/workspaces
  body: { name, slug, members?, teams_sync? }
  → [RequirePermission("workspaces:create")]
  → FluentValidation: name required, slug unique within tenant
  → CreateWorkspaceHandler
    → 1. Verify tenant has WorkSync enabled (feature flag check)
    → 2. Create Workspace entity
    → 3. Seed 3 system WorkspaceRole rows in same transaction:
         Admin (is_system=true), Member (is_system=true), Viewer (is_system=true)
    → 4. Add creator as Admin WorkspaceMember
    → 5. SaveChanges (transaction commits workspace + roles + member atomically)
    → 6. Publish WorkspaceCreatedEvent
    → Return Result<WorkspaceDto>
  → 201 Created
```

## Invite Workspace Member

## Microsoft Teams Workspace Sync

```
POST /api/v1/workspaces
  body.teams_sync: { create_team?, existing_team_id?, create_default_channel? }
  -> CreateWorkspaceHandler
    -> 1. Create workspace, roles, and members first
    -> 2. If create_team = true:
         a. Verify Microsoft Teams integration is enabled
         b. Verify required members have linked Teams accounts
         c. Create Microsoft Team/group through Graph
         d. Insert workspace_teams_links
         e. Link default ONEVO channel to Teams general channel
    -> 3. If existing_team_id is provided:
         a. Verify selected Team candidate and member match confirmation
         b. Insert workspace_teams_links
         c. Link selected channels if requested
    -> 4. If Teams operation fails after workspace commit:
         a. Keep workspace
         b. Mark Teams link status = failed
         c. Show retry action to workspace admin
```

## Microsoft Teams Eligibility

```
GET /api/v1/workspaces/{id}/teams/eligibility
  -> [RequirePermission("workspaces:manage")]
  -> WorkspaceTeamsEligibilityHandler
    -> 1. Load workspace members
    -> 2. Check each member's Microsoft Teams account link
    -> 3. Return all_members_linked, missing_members, can_create_team, can_link_existing_team
```

## Link Existing Microsoft Team

```
GET /api/v1/workspaces/{id}/teams/candidates
  -> Find Teams groups visible to caller
  -> Compare Teams members to workspace members
  -> Return match score and member differences

POST /api/v1/workspaces/{id}/teams/link
  -> [RequirePermission("workspaces:manage")]
  -> LinkExistingTeamHandler
    -> 1. Verify workspace has no active Teams link
    -> 2. Verify selected Team belongs to the tenant
    -> 3. Confirm member differences
    -> 4. Create workspace_teams_links
    -> 5. Optionally map ONEVO channels to Teams channels
```

```
POST /api/v1/workspaces/{id}/members
  → [RequirePermission("workspaces:manage")]
  → AddWorkspaceMemberHandler
    → 1. Verify workspace exists and belongs to tenant
    → 2. Verify user exists in tenant (must be a tenant user)
    → 3. Check user not already a member
    → 4. Resolve workspace_role_id from role name
    → 5. Create WorkspaceMember row
    → 6. Publish WorkspaceMemberAddedEvent
    → Return Result<WorkspaceMemberDto>
```

## Workspace Context Resolution (Every WorkSync Request)

```
Every WorkSync API request:
  → TenantResolutionMiddleware: resolve tenant_id from JWT sub claim
  → WorkspaceResolutionMiddleware:
      1. Read workspace_id from JWT claim "workspace_id"
         OR X-Workspace-Id header (header takes precedence)
      2. Verify user is member of workspace_id
      3. Set ICurrentWorkspace.WorkspaceId
  → Global query filters: WHERE tenant_id = ? AND workspace_id = ?
  → Handler executes with scoped workspace context
```

## Remove Member

```
DELETE /api/v1/workspaces/{id}/members/{userId}
  → [RequirePermission("workspaces:manage")]
  → RemoveWorkspaceMemberHandler
    → 1. Verify requester is workspace Admin
    → 2. Cannot remove yourself if you are the last Admin
    → 3. Soft-cascade: remove user from project_members in this workspace
    → 4. Delete WorkspaceMember row (hard delete — no soft delete for membership)
    → 5. Publish WorkspaceMemberRemovedEvent
```

### Error Scenarios

| Scenario | HTTP | Error |
|:---------|:-----|:------|
| Tenant does not have WorkSync | 403 | WorkSync not enabled for tenant |
| Slug not unique in tenant | 409 | Workspace slug already exists |
| User not in tenant | 404 | User not found |
| Already a member | 409 | User is already a workspace member |
| Remove last Admin | 422 | Workspace must have at least one Admin |
| Unknown workspace_id in header | 403 | Not a member of this workspace |
| Teams checkbox selected but tenant integration disabled | 422 | Microsoft Teams integration is not enabled |
| Some workspace members have no Teams link | 422 | Missing Teams account links |
| Workspace already has active Teams link | 409 | Workspace already linked to Teams |

## Related

- [[modules/work-management/foundation/overview|Foundation Overview]]
- [[modules/work-management/foundation/testing|Foundation Testing]]
- [[modules/integrations/microsoft-teams/end-to-end-logic|Microsoft Teams Integration Logic]]
