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
    -> 2. Validate name and tenant-unique identifier
         identifier: 2-6 uppercase letters, e.g. "TASK", "BUG"
    -> 3. Create Project entity with status = active
    -> 4. Add creator as project_members role = admin
    -> 5. Link any selected team workspaces through project_workspaces
    -> 6. Publish ProjectCreatedEvent
    -> Return Result<ProjectDto>
  -> 201 Created
```

Project creation does not make the project belong to exactly one workspace. A project can be linked to zero, one, or many workspaces through `project_workspaces`.

## Archive Project

```text
PATCH /api/v1/projects/{id}/archive
  -> [RequirePermission("projects:write") + project admin]
  -> ArchiveProjectHandler
    -> 1. Verify project status != archived
    -> 2. Check active sprint: if sprint status = active -> return 422
         "Complete active sprint before archiving project"
    -> 3. UPDATE projects.status = archived
    -> 4. Publish ProjectArchivedEvent
         -> Close open sprints, notify project members
    -> Return Result<ProjectDto>
```

## Manage Project Members

```text
POST /api/v1/projects/{id}/members
  -> [RequirePermission("projects:write") + project admin]
  -> AddProjectMemberHandler
    -> 1. Verify employee is active, non-deleted, and belongs to tenant
    -> 2. Verify user is not already an active project member
    -> 3. INSERT project_members with role = member by default
    -> Return 201

DELETE /api/v1/projects/{id}/members/{userId}
  -> [RequirePermission("projects:write") + project admin]
  -> RemoveProjectMemberHandler
    -> 1. Reject if this would remove the last active project admin
    -> 2. Deactivate project_members row
    -> Return 204
```

Project membership is the source of truth for project visibility. A user does not need full workspace membership to be added to a project.

## Link Project Workspaces

```text
POST /api/v1/projects/{id}/workspaces
  body: { workspace_id }
  -> [RequirePermission("projects:write") + project admin]
  -> LinkProjectWorkspaceHandler
    -> 1. Verify workspace belongs to same tenant
    -> 2. Verify link is not already active
    -> 3. INSERT project_workspaces
    -> 4. Do not add workspace members to project_members automatically
    -> Return 201

DELETE /api/v1/projects/{id}/workspaces/{workspaceId}
  -> [RequirePermission("projects:write") + project admin]
  -> UnlinkProjectWorkspaceHandler
    -> 1. Deactivate project_workspaces row
    -> 2. Preserve project_members unless explicitly removed
    -> Return 204
```

`project_workspaces` is context only. It supports team/workspace grouping, reporting, and member suggestions, but it does not expose the project to every member of the linked workspace.

## Change Project Admin

```text
PATCH /api/v1/projects/{id}/members/{userId}/role
  body: { role: "admin" | "member" | "viewer" }
  -> [RequirePermission("projects:write") + project admin]
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
| Archive with active sprint | 422 | Complete active sprint first |
| Add inactive employee | 422 | Employee is not active |
| Remove or demote last project admin | 422 | Project requires at least one active admin |
| Link workspace from another tenant | 403 | Workspace is outside tenant scope |

## Related

- [[modules/work-management/projects/overview|Projects Overview]]
- [[modules/work-management/projects/testing|Projects Testing]]
