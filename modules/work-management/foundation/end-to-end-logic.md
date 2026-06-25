# Work Foundation - End-to-End Logic

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
         a. manual_invite -> filter selected employees/members through active Company context and member-management authority
    -> 4. Create Workspace entity
    -> 5. Seed 3 system WorkspaceRole rows in same transaction:
         Admin, Member, Viewer
    -> 6. Add creator as local workspace administration member
    -> 7. Send invitations to selected members with selected workspace roles
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
         a. active Company context
         b. workspace/project member-management authority
         c. explicit project/workspace grants where supported
    -> 4. If target is outside authority, reject with scoped 403
    -> 5. Verify user exists in tenant and has an active employee record
    -> 6. Check user is not already a member or pending invite recipient
    -> 7. Resolve workspace_role_id from role name
    -> 8. Create workspace member invitation
    -> 9. Notify selected member through Inbox
    -> Return Result<WorkspaceMemberDto>
```

Workspace membership controls access to workspace-scoped resources. It does not automatically grant project access. Project visibility is controlled by `project_members`.

Reporting-manager relationship does not grant workspace member-management authority. Workspace membership and local workspace/project authority control Work access.

## Accept Workspace Member Invitation

```text
POST /api/v1/workspaces/{id}/member-invitations/{inviteId}/decision
  -> [Authenticated selected recipient]
  -> DecideWorkspaceMemberInvitationHandler
    -> 1. Verify invitation is pending and addressed to the current user/employee
    -> 2. If declined, mark invitation declined and stop
    -> 3. If accepted, create WorkspaceMember row with the invited local role
    -> 4. Publish WorkspaceMemberAddedEvent
    -> Return 204
```

Accepted workspace membership does not grant reporting authority or project access unless a project membership is separately created.

## Microsoft Teams Workspace Sync (Phase 2)

```text
POST /api/v1/workspaces
  body.teams_sync: { create_team?, existing_team_id?, create_default_channel? }
  -> CreateWorkspaceHandler
    -> 1. Create workspace, roles, and members first
    -> 2. If create_team = true:
         a. Verify Microsoft Teams integration is enabled
         d. Insert workspace_teams_links
    -> 3. If existing_team_id is provided:
         b. Insert workspace_teams_links
         c. Link selected channels if requested
         a. Keep workspace
         c. Show retry action to workspace admin
```

## Microsoft Teams Eligibility (Phase 2)

```text
  -> [RequirePermission("workspaces:manage")]
  -> WorkspaceTeamsEligibilityHandler
    -> 1. Load workspace members
    -> 2. Check each member's Microsoft Teams account link
    -> 3. Return all_members_linked, missing_members, can_create_team, can_link_existing_team
```


```text
  -> Return match score and member differences

  -> [RequirePermission("workspaces:manage")]
  -> LinkExistingTeamHandler
    -> 3. Confirm member differences
    -> 4. Create workspace_teams_links
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

## Related

- [[modules/work-management/foundation/overview|Foundation Overview]]
- [[modules/work-management/foundation/testing|Foundation Testing]]
- [[modules/integrations/microsoft-teams/end-to-end-logic|Microsoft Teams Integration Logic]]
