# WorkSync Foundation - End-to-End Logic

**Module:** WorkSync
**Feature:** Foundation

---

## Create Workspace

```text
POST /api/v1/workspaces
  body: { name, slug, member_source, members?, teams_sync? }
  -> [RequirePermission("workspaces:create")]
  -> FluentValidation: name required, slug unique within tenant
  -> CreateWorkspaceHandler
    -> 1. Verify tenant has WorkSync enabled
    -> 2. Resolve active legal entity context
    -> 3. Resolve member source:
         a. my_reporting_team -> query employee_hierarchy_closure
         b. explicit_team -> validate caller can use stored Org Structure team
         c. manual_invite -> filter selected employees through allowed member pool
    -> 4. Create Workspace entity
    -> 5. Seed 3 system WorkspaceRole rows in same transaction:
         Admin, Member, Viewer
    -> 6. Add creator as local workspace administration member
    -> 7. Add resolved members with selected workspace roles
    -> 8. If source is my_reporting_team, do not create teams/team_members
    -> 9. SaveChanges
    -> 10. Publish WorkspaceCreatedEvent
    -> Return Result<WorkspaceDto>
  -> 201 Created
```

## Invite Workspace Member

```text
POST /api/v1/workspaces/{id}/members
  -> [RequirePermission("workspaces:manage")]
  -> AddWorkspaceMemberHandler
    -> 1. Verify workspace exists and belongs to tenant
    -> 2. Verify caller has local workspace member-management authority
    -> 3. Resolve caller's allowed member pool:
         a. position-derived hierarchy for scoped managers
         b. legal-entity/organization scope for broader authorized users
         c. explicit bypass grants
    -> 4. If target is outside allowed pool, create participation request instead of direct add
    -> 5. Verify user exists in tenant and has an active employee record
    -> 6. Check user is not already a member
    -> 7. Resolve workspace_role_id from role name
    -> 8. Create WorkspaceMember row
    -> 9. Publish WorkspaceMemberAddedEvent
    -> Return Result<WorkspaceMemberDto>
```

Workspace membership controls access to workspace-scoped resources. It does not automatically grant project access. Project visibility is controlled by `project_members`.

Hierarchy authority is not global. A reporting manager can add reports to a workspace they control, but cannot use reporting hierarchy alone to manage those reports inside another workspace.

## Request Outside Workspace Member

```text
POST /api/v1/workspaces/{id}/member-requests
  -> [RequirePermission("workspaces:manage") + local workspace member-management authority]
  -> RequestWorkspaceMemberHandler
    -> 1. Verify target employee is outside caller's direct add pool
    -> 2. Resolve approval target through configured resolver:
         target employee's reporting chain, target workspace owner,
         legal-entity approver, selected permission, or specific employee
    -> 3. Create participation request
    -> 4. Send Inbox/Chat action card
    -> Return 202 Accepted
```

Approval adds the employee as a workspace member only. It does not grant reporting authority or project access unless a project membership is separately created.

## Microsoft Teams Workspace Sync

```text
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

```text
GET /api/v1/workspaces/{id}/teams/eligibility
  -> [RequirePermission("workspaces:manage")]
  -> WorkspaceTeamsEligibilityHandler
    -> 1. Load workspace members
    -> 2. Check each member's Microsoft Teams account link
    -> 3. Return all_members_linked, missing_members, can_create_team, can_link_existing_team
```

## Link Existing Microsoft Team

```text
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

## Workspace Context Resolution

```text
Workspace-scoped WorkSync API request:
  -> TenantResolutionMiddleware resolves tenant_id from session/JWT
  -> WorkspaceResolutionMiddleware:
      1. Read workspace_id from backend session or X-Workspace-Id header
      2. Verify user is an active workspace member
      3. Set ICurrentWorkspace.WorkspaceId
  -> Handler executes with tenant + workspace context
```

Project-scoped requests do not require one active workspace context. They resolve access from `project_members`. They use `project_workspaces` only when an action needs team/workspace context, such as grouping tasks or selecting suggested members.

## Remove Member

```text
DELETE /api/v1/workspaces/{id}/members/{userId}
  -> [RequirePermission("workspaces:manage")]
  -> RemoveWorkspaceMemberHandler
    -> 1. Verify requester has local workspace member-management authority
    -> 2. Cannot remove yourself if you are the last local workspace administrator
    -> 3. Delete WorkspaceMember row
    -> 4. Re-evaluate workspace-scoped access only
    -> 5. Do not remove project_members automatically
    -> 6. Publish WorkspaceMemberRemovedEvent
```

## Error Scenarios

| Scenario | HTTP | Error |
|:---------|:-----|:------|
| Tenant does not have WorkSync | 403 | WorkSync not enabled for tenant |
| Slug not unique in tenant | 409 | Workspace slug already exists |
| User not in tenant | 404 | User not found |
| Already a member | 409 | User is already a workspace member |
| Remove last local workspace administrator | 422 | Workspace must have at least one local administrator |
| Unknown workspace_id in header | 403 | Not a member of this workspace |
| Teams checkbox selected but tenant integration disabled | 422 | Microsoft Teams integration is not enabled |
| Some workspace members have no Teams link | 422 | Missing Teams account links |
| Workspace already has active Teams link | 409 | Workspace already linked to Teams |

## Related

- [[modules/work-management/foundation/overview|Foundation Overview]]
- [[modules/work-management/foundation/testing|Foundation Testing]]
- [[modules/integrations/microsoft-teams/end-to-end-logic|Microsoft Teams Integration Logic]]
