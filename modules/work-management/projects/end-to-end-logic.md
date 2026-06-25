# Project Management - End-to-End Logic

**Module:** WorkSync
**Feature:** Project Management

---

## Create Project

```text
POST /api/v1/projects
  -> [RequirePermission("projects:create")]
  -> CreateProjectHandler
    -> 1. Validate caller can create projects in the tenant/module boundary
    -> 2. Resolve owning_legal_entity_id from active legal entity context
    -> 3. Resolve workspace_id from selected workspace context and verify caller has workspace/project creation authority
    -> 4. Validate name and tenant-unique identifier
         identifier: 2-6 uppercase letters, e.g. "TASK", "BUG"
    -> 5. Create Project entity with status = active and the resolved workspace_id
    -> 6. Add creator as project_members with project-local administration access
    -> 7. Do not create workspace participation links in Phase 1
    -> 8. Publish ProjectCreatedEvent
    -> Return Result<ProjectDto>
  -> 201 Created
```

Project creation is simple in Phase 1: one project, one workspace, active legal entity context, creator as project admin, and accepted direct project membership. Workspace participation links and workspace source pools are Phase 2 references.

## Archive Project

```text
PATCH /api/v1/projects/{id}/archive
  -> [RequirePermission("projects:write") + project-local administration access]
  -> ArchiveProjectHandler
    -> 1. Verify project status != archived
    -> 2. UPDATE projects.status = archived
    -> 3. Publish ProjectArchivedEvent
         -> Notify project members and block new Phase 1 work item creation
    -> Return Result<ProjectDto>
```

## Invite And Manage Project Members

```text
POST /api/v1/projects/{id}/member-invitations
  -> [RequirePermission("projects:write") + project-local administration access]
  -> InviteProjectMemberHandler
    -> 1. Verify employee is active, non-deleted, and belongs to tenant
    -> 2. Verify user is not already an active project member or pending invite recipient
    -> 3. INSERT project_member_invitations with role = member by default
    -> 4. Notify selected member through Inbox
    -> Return 202

POST /api/v1/projects/{id}/member-invitations/{inviteId}/decision
  -> [Authenticated selected recipient]
  -> DecideProjectMemberInvitationHandler
    -> 1. Verify invitation is pending and addressed to current user/employee
    -> 2. If declined, mark invitation declined and stop
    -> 3. If accepted, INSERT project_members with invited role
    -> Return 204

DELETE /api/v1/projects/{id}/members/{userId}
  -> [RequirePermission("projects:write") + project-local administration access]
  -> RemoveProjectMemberHandler
    -> 1. Reject if this would remove the last active project admin
    -> 2. Deactivate project_members row
    -> Return 204
```

Project membership is the source of truth for project visibility. A user does not need full workspace membership to be invited to a project, but the selected member must accept before project access becomes active.

## Link Projects - Phase 1 Simple Invite

This flow creates an informational/simple project-link record after both project admins agree. It is not an advanced dependency or cross-workspace source-pool platform.

```text
POST /api/v1/projects/{id}/link-invitations
  body: { target_project_id, link_type? }
  -> [RequirePermission("projects:write") + project-local administration access]
  -> InviteProjectLinkHandler
    -> 1. Verify target project belongs to same tenant or allowed connected-company scope where supported
    -> 2. Resolve target project admin recipient
    -> 3. INSERT project_link_invitations with status = pending
    -> 4. Notify target project admin through Inbox
    -> Return 202

POST /api/v1/projects/{id}/link-invitations/{inviteId}/decision
  -> [Authenticated target project admin]
  -> DecideProjectLinkInvitationHandler
    -> 1. Verify invite is pending and addressed to the target project admin
    -> 2. If declined, mark invitation declined and stop
    -> 3. If accepted, INSERT project_links
    -> Return 204
```

## Link Project Workspaces - Phase 2 Reference

This flow is not active Phase 1 behavior. Phase 1 project visibility is controlled by accepted direct `project_members` rows and scoped project permissions.

```text
POST /api/v1/projects/{id}/workspaces
  -> Phase 2 only
```

Workspace participation approvals, linked workspace source pools, and owner-to-owner project participation governance are Phase 2 reference behavior.

## Change Project Local Access

```text
PATCH /api/v1/projects/{id}/members/{userId}/role
  body: { role: "admin" | "member" | "viewer" }
  -> [RequirePermission("projects:write") + project-local administration access]
  -> ChangeProjectMemberRoleHandler
    -> 1. Verify target member is active
    -> 2. Reject if demoting/removing would leave project with zero admins
    -> 3. UPDATE project_members.role
    -> Return 204
```

## Error Scenarios

| Scenario | HTTP | Error |
|:---------|:-----|:------|
| Identifier not unique | 409 | Project identifier already in use |
| Archive project | 200 | Project archived; new Phase 1 work item creation is blocked |
| Add inactive employee | 422 | Employee is not active |
| Remove or demote last project-local administrator | 422 | Project requires at least one active local administrator |
| Missing workspace context | 422 | Select a workspace before creating the project |
| Workspace linking attempted | 403 | Phase 2 workspace linking is not active in Phase 1 |

## Related

- [[modules/work-management/projects/overview|Projects Overview]]
- [[modules/work-management/projects/testing|Projects Testing]]
